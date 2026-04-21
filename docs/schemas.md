# Schemas Overview

This project uses JSON Schemas in the `schemas/` folder.

- `schemas/user.schema.json`
- `schemas/project.schema.json`
- `schemas/dataset.schema.json`
- `schemas/observation.schema.json`
- `schemas/score.schema.json`

## Validation Notes

- `project_id`, `dataset_id`, and `observation_id` are required linkage keys.
- `score_value` must be numeric and constrained by business logic at service layer.
