import parlant.sdk as p

from jose import jwt
from jose.exceptions import JWTError as JWTDecodeError
from fastapi import HTTPException,Request
from limits import RateLimitItemPerMinute, RateLimitItemPerHour
from limits.storage import RedisStorage
from limits.strategies import SlidingWindowCounterRateLimiter
import traceback

class CustomAuthorizationPolicy(p.ProductionAuthorizationPolicy):
    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        super().__init__()
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.default_limiter = p.BasicRateLimiter(
            rate_limit_item_per_operation={
                # Use the default rate limit for most operations
                **self.default_limiter.rate_limit_item_per_operation,
                # Override specific operations with custom limits
                p.Operation.READ_SESSION: RateLimitItemPerMinute(200),
                p.Operation.LIST_EVENTS: RateLimitItemPerMinute(1000),
            },
            # Use a custom storage backend (e.g., Redis)
            storage=RedisStorage("redis://localhost:6379"),
            # Use a custom window strategy
            limiter_type=SlidingWindowCounterRateLimiter,
        )

    async def _extract_token(self, request: Request) -> dict | None:
        """Extract and validate JWT token from request"""
        print(request.headers)
        auth_header = request.headers.get("authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None

        token = auth_header.split(" ")[1]
        print(token)
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            print(payload)
            return payload
        except JWTDecodeError:
            traceback.print_exc()
            # Raise 403 for invalid tokens, None for missing tokens is OK
            raise HTTPException(
                status_code=403,
                detail="Invalid access token"
            )

    async def check_permission(
        self,
        request: Request,
        operation: p.Operation
    ) -> bool:
        """Enhanced permission checking with M2M token support"""
        return True
        token_payload = await self._extract_token(request)
        print(token_payload)
        print(operation.name)
        print(token_payload.get("type") if token_payload else "No Token")

        # If we have a valid M2M (machine-to-machine) token, allow additional operations
        if token_payload and token_payload.get("type") == "m2m":
            m2m_operations = {
                # Allow M2M tokens to perform administrative operations
                p.Operation.CREATE_AGENT,
                p.Operation.READ_AGENT,
                p.Operation.UPDATE_AGENT,
                p.Operation.DELETE_AGENT,
                p.Operation.CREATE_CUSTOMER,
                p.Operation.READ_CUSTOMER,
                p.Operation.UPDATE_CUSTOMER,
                p.Operation.DELETE_CUSTOMER,
                p.Operation.CREATE_CUSTOMER_SESSION,
                p.Operation.LIST_SESSIONS,
                p.Operation.UPDATE_SESSION,
                p.Operation.DELETE_SESSION,
                p.Operation.LIST_CUSTOMERS
                # Add other operations your M2M integration needs
            }

            if operation in m2m_operations:
                print("M2M operation allowed:", operation.name)
                return True

        # For all other cases, delegate to the parent ProductionAuthorizationPolicy
        print("Delegating to parent check_permission")
        return await super().check_permission(request, operation)
    
