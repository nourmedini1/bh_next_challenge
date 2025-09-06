# Copyright 2025 Emcie Co Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations
import time
import json
import jsonfinder  # type: ignore
import os
from typing import Any, Mapping
from typing_extensions import override

from mistralai import Mistral  # type: ignore
from mistralai.models import (  # type: ignore
    ChatCompletionRequest,
    ResponseFormat,
    ResponseFormats,
)
from pydantic import ValidationError
import tiktoken  # We'll use tiktoken as an approximation for token counting

from parlant.adapters.nlp.common import normalize_json_output
from parlant.core.engines.alpha.canned_response_generator import (
    CannedResponseDraftSchema,
    CannedResponseSelectionSchema,
)
from parlant.core.engines.alpha.guideline_matching.generic.journey_node_selection_batch import (
    JourneyNodeSelectionSchema,
)
from parlant.core.engines.alpha.prompt_builder import PromptBuilder
from parlant.core.engines.alpha.tool_calling.single_tool_batch import SingleToolBatchSchema
from parlant.core.loggers import LogLevel, Logger
from parlant.core.nlp.policies import policy, retry
from parlant.core.nlp.tokenization import EstimatingTokenizer
from parlant.core.nlp.service import NLPService
from parlant.core.nlp.embedding import Embedder, EmbeddingResult
from parlant.core.nlp.generation import (
    T,
    SchematicGenerator,
    SchematicGenerationResult,
)
from parlant.core.nlp.generation_info import GenerationInfo, UsageInfo
from parlant.core.nlp.moderation import ModerationCheck, ModerationService


class MistralEstimatingTokenizer(EstimatingTokenizer):
    def __init__(self, model_name: str) -> None:
        self.model_name = model_name
        # Use GPT-4 tokenizer as approximation since Mistral uses similar tokenization
        self.encoding = tiktoken.encoding_for_model("gpt-4")

    @override
    async def estimate_token_count(self, prompt: str) -> int:
        tokens = self.encoding.encode(prompt)
        return len(tokens)


class MistralSchematicGenerator(SchematicGenerator[T]):
    supported_mistral_params = ["temperature", "max_tokens", "top_p", "random_seed"]

    def __init__(
        self,
        model_name: str,
        logger: Logger,
    ) -> None:
        self.model_name = model_name
        self._logger = logger

        api_key = os.environ.get("MISTRAL_SERVICE_API_KEY" )
        if not api_key:
            raise ValueError("MISTRAL_SERVICE_API_KEY environment variable is required")

        self._client = Mistral(api_key=api_key)
        self._tokenizer = MistralEstimatingTokenizer(model_name=self.model_name)

    @property
    @override
    def id(self) -> str:
        return f"mistral/{self.model_name}"

    @property
    @override
    def tokenizer(self) -> MistralEstimatingTokenizer:
        return self._tokenizer

    @policy(
        [
            retry(
                exceptions=(
                    Exception,  # Mistral SDK might throw various exceptions
                ),
                max_exceptions=3,
                wait_times=(1.0, 2.0, 4.0),
            ),
        ]
    )
    @override
    async def generate(
        self,
        prompt: str | PromptBuilder,
        hints: Mapping[str, Any] = {},
    ) -> SchematicGenerationResult[T]:
        with self._logger.scope("MistralSchematicGenerator"):
            with self._logger.operation(
                f"LLM Request ({self.schema.__name__})", level=LogLevel.TRACE
            ):
                return await self._do_generate(prompt, hints)

    async def _do_generate(
        self,
        prompt: str | PromptBuilder,
        hints: Mapping[str, Any] = {},
    ) -> SchematicGenerationResult[T]:
        if isinstance(prompt, PromptBuilder):
            prompt = prompt.build()

        mistral_api_arguments = {k: v for k, v in hints.items() if k in self.supported_mistral_params}

        try:
            t_start = time.time()
            
            # Use JSON mode for structured output
            response = await self._client.chat.complete_async(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type" : "json_object"},
                **mistral_api_arguments,
            )
            
            t_end = time.time()
        except Exception as e:
            self._logger.error(f"Mistral API error: {e}")
            raise

        if response.usage:
            self._logger.trace(f"Usage: {response.usage}")

        raw_content = response.choices[0].message.content or "{}"

        try:
            json_content = json.loads(normalize_json_output(raw_content))
        except json.JSONDecodeError:
            self._logger.warning(f"Invalid JSON returned by {self.model_name}:\n{raw_content})")
            try:
                json_content = jsonfinder.only_json(raw_content)[2]
                self._logger.warning("Found JSON content within model response; continuing...")
            except Exception:
                self._logger.error("Could not extract valid JSON from response")
                raise

        try:
            content = self.schema.model_validate(json_content)

            usage_info = UsageInfo(
                input_tokens=response.usage.prompt_tokens if response.usage else 0,
                output_tokens=response.usage.completion_tokens if response.usage else 0,
            )

            return SchematicGenerationResult(
                content=content,
                info=GenerationInfo(
                    schema_name=self.schema.__name__,
                    model=self.id,
                    duration=(t_end - t_start),
                    usage=usage_info,
                ),
            )

        except ValidationError as e:
            self._logger.error(
                f"Error: {e.json(indent=2)}\nJSON content returned by {self.model_name} does not match expected schema:\n{raw_content}"
            )
            raise


class MistralSmall(MistralSchematicGenerator[T]):
    def __init__(self, logger: Logger) -> None:
        super().__init__(model_name="mistral-small-latest", logger=logger)

    @property
    @override
    def max_tokens(self) -> int:
        return 32768  # Mistral Small context window


class MistralEmbedder(Embedder):
    def __init__(self, model_name: str, logger: Logger) -> None:
        self.model_name = model_name
        self._logger = logger

        api_key =     "G5EZuXx1bWCghEj5VaaQ8TwajQ9nav6g"
        if not api_key:
            raise ValueError("MISTRAL_API_KEY environment variable is required")
        
        self._client = Mistral(api_key=api_key)
        self._tokenizer = MistralEstimatingTokenizer(model_name=self.model_name)

    @property
    @override
    def id(self) -> str:
        return f"mistral/{self.model_name}"

    @property
    @override
    def tokenizer(self) -> MistralEstimatingTokenizer:
        return self._tokenizer

    @property
    @override
    def max_tokens(self) -> int:
        return 8192  # Mistral embedding model context window

    @property
    @override
    def dimensions(self) -> int:
        return 1024  # Mistral embed model dimensions

    @policy(
        [
            retry(
                exceptions=(Exception,),
                max_exceptions=3,
                wait_times=(1.0, 2.0, 4.0),
            ),
        ]
    )
    @override
    async def embed(
        self,
        texts: list[str],
        hints: Mapping[str, Any] = {},
    ) -> EmbeddingResult:
        try:
            response = await self._client.embeddings.create_async(
                model=self.model_name,
                inputs=texts,
            )
        except Exception as e:
            self._logger.error(f"Mistral Embedding API error: {e}")
            raise

        vectors = [data_point.embedding for data_point in response.data]
        return EmbeddingResult(vectors=vectors)


class MistralTextEmbedding(MistralEmbedder):
    def __init__(self, logger: Logger) -> None:
        super().__init__(model_name="mistral-embed", logger=logger)


class NoModerationService(ModerationService):
    """Simple pass-through moderation service that flags nothing."""
    
    @override
    async def check(self, content: str) -> ModerationCheck:
        return ModerationCheck(flagged=False, tags=[])


class MistralService(NLPService):
    def __init__(
        self,
        logger: Logger,
    ) -> None:
        self._logger = logger
        self._logger.info("Initialized MistralService")

    @override
    async def get_schematic_generator(self, t: type[T]) -> MistralSchematicGenerator[T]:
        # Use MistralSmall for all schema types
        # You can customize this mapping based on your needs
        return MistralSmall[t](self._logger)  # type: ignore

    @override
    async def get_embedder(self) -> Embedder:
        return MistralTextEmbedding(self._logger)

    @override
    async def get_moderation_service(self) -> ModerationService:
        # Mistral doesn't have a built-in moderation service, so we use a no-op implementation
        # You could integrate with another moderation service here if needed
        return NoModerationService()


# Convenience function to load the service
def load_mistral_service(container) -> MistralService:
    """Factory function to create MistralService with proper dependencies."""
    import parlant.sdk as p
    return MistralService(
        logger=container[p.Logger]
    )