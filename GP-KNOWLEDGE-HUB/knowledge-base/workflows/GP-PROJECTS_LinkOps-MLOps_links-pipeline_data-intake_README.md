# whis_data_input

This is the whis_data_input microservice in the LinkOps MLOps platform.

## Responsibilities
- Receive and validate raw input tasks/questions from human engineers
- Store high-confidence task/solution pairs for training
- Prepare data for the sanitization pipeline

## Endpoints
- `GET /` - Service status
- `GET /health` - Health check
- `POST /input` - Submit new training data 