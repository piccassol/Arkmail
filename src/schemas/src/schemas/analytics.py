from pydantic import BaseModel

class EmailAnalyticsResponse(BaseModel):
    openRate: float
    clickRate: float
    bounceRate: float
    unsubscribeRate: float
