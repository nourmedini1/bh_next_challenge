from datetime import datetime
import parlant.sdk as p
from typing import Any
from security.security_check import is_malicious_or_violation
from security.authorization_policy import CustomAuthorizationPolicy
from observability.log_producer import LogProducer


security_log_producer = LogProducer(bootstrap_servers="localhost:9092", client_id="security-log-producer")



async def intercept_message_generation_with_security_check(
    ctx: p.LoadedContext, payload: Any, exc: Exception | None
) -> p.EngineHookResult:
    message = ctx.interaction.last_customer_message.content
    start_time = datetime.now()
    response = await is_malicious_or_violation(message)
    end_time = datetime.now()
    response_time_ms = (end_time - start_time).total_seconds() * 1000  # Convert to milliseconds
    if response.get("status", "REJECTED") == "REJECTED":
        message = "Your Message has been flagged for review."
        details = response.get("details", [])
        if details:
            is_prompt_injection = details[0].get("result", {}).get("is_injection", False)
            if is_prompt_injection:
                message += f" \nPotential prompt injection attempt was detected in your message."
            is_content_violation = details[1].get("result", {}).get("has_violations", False)
            if is_content_violation:
                message += f" \nContent violation was detected in your message : {details[1].get('result', {}).get('explanation', [])} with severity {details[1].get('result', {}).get('severity', 'unknown')}."
        security_log = {
            'timestamp': start_time.isoformat(),
            'message': message,
            'details': response.get("details", []),
            'status': 'REJECTED',
            'response_time_ms': response_time_ms
        }
        security_log_producer.send("security_logs", security_log)
        await ctx.session_event_emitter.emit_message_event(
            correlation_id=ctx.correlator.correlation_id,
            data=message
        )
        return p.EngineHookResult.BAIL  
    else:
        return p.EngineHookResult.CALL_NEXT 
    
async def configure_hooks(hooks: p.EngineHooks) -> p.EngineHooks:
    hooks.on_acknowledged.append(intercept_message_generation_with_security_check)
    return hooks

async def configure_container(
    container: p.Container
) -> p.Container:
    container[p.AuthorizationPolicy] = CustomAuthorizationPolicy(
        secret_key="your-secret-key-change-in-production",
        algorithm="HS256",
    )

    return container
