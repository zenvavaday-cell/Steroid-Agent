---
name: api-contract-validation
description: Validates OpenAPI, JSON Schema, GraphQL, and protobuf contracts, detects breaking changes against a baseline, runs consumer-driven contract tests, and checks examples, status codes, and error shapes. Use for API design review, versioning, SDK generation, and pre-merge compatibility gates.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: engineering
---

# API Contract Validation

## Overview

An API contract is a promise to consumers. Validation has three layers: the contract is well-formed, the implementation matches it, and the change is compatible with existing consumers. Most tools check only the first two.

This skill covers schema linting, example validation, breaking-change detection, and contract testing.

## When to use

- Reviewing an API change before merge.
- Adding a compatibility gate to CI.
- Generating or updating an SDK.
- Auditing an undocumented or inconsistent API.
- Designing a new version.

## Workflow

### 1. Locate the source of truth

| Style | Contract |
| --- | --- |
| REST | OpenAPI 3.x YAML/JSON |
| GraphQL | SDL schema |
| gRPC | `.proto` files |
| Events | AsyncAPI or JSON Schema |
| Webhooks | OpenAPI callbacks or payload schemas |

If the code is the source of truth, generate the contract and compare. If the contract is the source, verify the implementation matches it.

### 2. Lint the contract

```bash
spectral lint openapi.yaml --ruleset .spectral.yaml
redocly lint openapi.yaml
buf lint
```

Check:

- Valid version and required fields.
- Unique operation IDs.
- Consistent naming and casing.
- Every operation has responses, including errors.
- Security schemes are declared and applied.
- Examples are present and valid.

### 3. Validate examples and schemas

```bash
openapi-generator validate -i openapi.yaml
ajv validate -s schema.json -d examples/*.json
```

Examples catch schema mistakes that linting misses: wrong types, missing required fields, invalid date formats, and inconsistent enums.

### 4. Detect breaking changes against a baseline

```bash
oasdiff breaking old.yaml new.yaml --fail-on ERR
buf breaking --against '.git#branch=main'
graphql-inspector diff old.graphql new.graphql
```

Classify:

| Change | Compatibility |
| --- | --- |
| Add optional request field | Usually compatible |
| Add response field | Usually compatible, but strict clients may break |
| Add enum value | Breaking for exhaustive clients |
| Remove or rename field | Breaking |
| Change type or format | Breaking |
| Make optional field required | Breaking |
| Change default | Behavioral breaking change |
| Change status code | Breaking |
| Remove endpoint or method | Breaking |
| Change authentication | Breaking |
| Tighten validation | Breaking for existing valid requests |

“Additive is safe” is not a universal rule. Enums, closed schemas, and strict deserializers break on additions.

### 5. Test the implementation against the contract

Use a schema-driven test or a mock server:

```bash
# Run a mock from the contract and test the client
prism mock openapi.yaml

# Validate live responses against the schema
schemathesis run https://api.example.com/openapi.json \
  --checks all --hypothesis-max-examples 50
```

Check:

- Status codes match the documented set.
- Response bodies validate against the schema.
- Error responses use the documented shape.
- Content types match.
- Pagination, filtering, and sorting behave as documented.
- Auth failures return the documented codes.

### 6. Run consumer-driven contract tests

For services with known consumers, use Pact or an equivalent:

```bash
pact-broker publish pacts/ --consumer-app-version "$GIT_SHA" \
  --broker-base-url "$PACT_BROKER_URL"
pact-broker can-i-deploy --pacticipant orders --version "$GIT_SHA" \
  --to-environment production
```

This catches the case where the provider is internally consistent but a consumer depends on a field or behavior being removed.

### 7. Gate and document

- Fail CI on breaking changes without a version bump.
- Require a deprecation window and a migration note.
- Publish the contract and a changelog.
- Version explicitly: URL path, header, or media type. Pick one strategy.

## Gotchas

- `nullable: true` and “optional” are different. A missing field and a null value are not interchangeable.
- JSON Schema `additionalProperties: false` makes additive changes breaking.
- Date-time formats need a timezone. A local timestamp is ambiguous.
- Integer versus number matters for clients in typed languages.
- Error shapes are part of the contract. A generic 500 with an HTML body breaks JSON clients.
- gRPC field numbers are forever. Never reuse a removed field number; reserve it.
- Protobuf `optional` presence semantics differ between proto2 and proto3.
- GraphQL nullability changes are breaking in both directions for different clients.
- SDK generation can hide breaking changes behind a regenerated client. Check the generated diff.
- A green schema validation does not prove business correctness. Test behavior too.

## Output contract

```json
{
  "contract": "openapi.yaml",
  "version": "2026-11-24",
  "lint": {"errors": 0, "warnings": 3},
  "examples_valid": true,
  "breaking_changes": [
    {
      "path": "/orders/{id}",
      "method": "GET",
      "change": "response field `legacy_status` removed",
      "compatibility": "breaking",
      "action": "restore field or bump major version"
    }
  ],
  "contract_tests": {"passed": 42, "failed": 0},
  "decision": "block_merge"
}
```

## Checklist

- [ ] Source of truth identified.
- [ ] Contract linted.
- [ ] Examples validated.
- [ ] Breaking changes diffed against the baseline.
- [ ] Implementation tested against the contract.
- [ ] Consumer contracts verified.
- [ ] Versioning and deprecation documented.
- [ ] CI gate enforces compatibility.

## Related skills

- `automated-pull-request-review` for reviewing the API diff.
- `schema-enforced-json-extraction` for runtime schema validation.
- `test-driven-verification-loop` for contract tests.
