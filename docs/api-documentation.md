# API Documentation

Base URL: `/api/v1`

## Health

### GET `/health`

- Description: Service health check.
- Response 200:

```json
{
  "status": "ok",
  "service": "terrascore-api"
}
```

## Projects

### GET `/projects`

- Description: List all projects.
- Response 200:

```json
[
  {
    "project_id": "proj_001",
    "project_name": "Northeast Flood Risk",
    "region": "India-Northeast"
  }
]
```

### POST `/projects`

- Description: Create a project.
- Request:

```json
{
  "project_name": "Northeast Flood Risk",
  "region": "India-Northeast"
}
```

- Response 201:

```json
{
  "project_id": "proj_001",
  "project_name": "Northeast Flood Risk",
  "region": "India-Northeast"
}
```

## Datasets

### GET `/datasets`

- Description: List configured datasets and access status.
- Response 200:

```json
[
  {
    "dataset_id": "gee_001",
    "source_name": "Google Earth Engine",
    "status": "blocked"
  }
]
```

### POST `/datasets/verify`

- Description: Mark dataset verification state.
- Request:

```json
{
  "dataset_id": "gee_001",
  "verification_state": "verified"
}
```

- Response 200:

```json
{
  "dataset_id": "gee_001",
  "status": "verified"
}
```

## Scoring

### POST `/scores/compute`

- Description: Compute score for a project.
- Request:

```json
{
  "project_id": "proj_001"
}
```

- Response 200:

```json
{
  "score_id": "score_001",
  "project_id": "proj_001",
  "score_value": 78.4,
  "score_band": "medium"
}
```
