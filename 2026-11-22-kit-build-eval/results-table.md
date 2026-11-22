## Screening (haiku, deepseek; 2 runs per cell)

Passes / runs for each check, none arm vs kit arm.

| task | check | haiku none | haiku kit | deepseek none | deepseek kit | all none | all kit |
|---|---|---|---|---|---|---|---|
| t1 | output_schema_rejects_wrong | 0/2 | 0/2 | 0/2 | 2/2 | 0/4 | 2/4 |
| t1 | retry_no_duplicate | 2/2 | 2/2 | 2/2 | 2/2 | 4/4 | 4/4 |
| t1 | annotations_match | 2/2 | 2/2 | 2/2 | 2/2 | 4/4 | 4/4 |
| t2 | write_without_token_401 | 2/2 | 2/2 | 2/2 | 2/2 | 4/4 | 4/4 |
| t2 | discovery_without_token | 2/2 | 2/2 | 1/2 | 2/2 | 3/4 | 4/4 |
| t2 | one_consistent_rule | 2/2 | 2/2 | 2/2 | 2/2 | 4/4 | 4/4 |
| t3 | one_structured_line_per_call | 2/2 | 2/2 | 2/2 | 2/2 | 4/4 | 4/4 |
| t3 | no_personal_data_in_logs | 2/2 | 2/2 | 2/2 | 2/2 | 4/4 | 4/4 |
| t4 | catches_output_schema_mismatch | 2/2 | 2/2 | 2/2 | 2/2 | 4/4 | 4/4 |
| t4 | catches_refusal_as_protocol_error | 2/2 | 2/2 | 2/2 | 2/2 | 4/4 | 4/4 |
| t4 | catches_missing_tool | 2/2 | 2/2 | 2/2 | 2/2 | 4/4 | 4/4 |
| t5 | valid_server_json | 2/2 | 2/2 | 2/2 | 2/2 | 4/4 | 4/4 |
| t5 | description_le_100 | 2/2 | 2/2 | 2/2 | 2/2 | 4/4 | 4/4 |
| t5 | github_org_namespace | 2/2 | 2/2 | 2/2 | 2/2 | 4/4 | 4/4 |
| t5 | version_matches | 2/2 | 2/2 | 2/2 | 2/2 | 4/4 | 4/4 |
| t5 | mcpname_matches | 2/2 | 2/2 | 2/2 | 2/2 | 4/4 | 4/4 |
| t5 | readme_read_org_token | 0/2 | 2/2 | 0/2 | 2/2 | 0/4 | 4/4 |

### Screening decision (keep rule from plan.md)

- **t1: KEEP**. t1a haiku: none fails (0/2); t1a deepseek: kit 2/2 > none 0/2; t1a deepseek: none fails (0/2)
- **t2: KEEP**. t2a deepseek: kit 2/2 > none 1/2; t2a deepseek: none fails (1/2)
- **t3: DROP**. Both arms pass every check in both lanes: nothing to measure.
- **t4: DROP**. Both arms pass every check in both lanes: nothing to measure.
- **t5: KEEP**. t5f haiku: kit 2/2 > none 0/2; t5f haiku: none fails (0/2); t5f deepseek: kit 2/2 > none 0/2; t5f deepseek: none fails (0/2)

## Full round (5 lanes, 3 runs per cell)

Passes / runs for each check, none arm vs kit arm.

| task | check | haiku none | haiku kit | sonnet none | sonnet kit | codex none | codex kit | deepseek none | deepseek kit | kimi none | kimi kit | all none | all kit |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| t1 | output_schema_rejects_wrong | 0/3 | 1/3 | 0/3 | 1/3 | 0/3 | 3/3 | 0/3 | 3/3 | 0/3 | 2/3 | 0/15 | 10/15 |
| t1 | retry_no_duplicate | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 15/15 | 15/15 |
| t1 | annotations_match | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 15/15 | 15/15 |
| t2 | write_without_token_401 | 3/3 | 3/3 | 0/3 | 1/3 | 0/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 9/15 | 13/15 |
| t2 | discovery_without_token | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 15/15 | 15/15 |
| t2 | one_consistent_rule | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 15/15 | 15/15 |
| t3 | one_structured_line_per_call | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 15/15 | 15/15 |
| t3 | no_personal_data_in_logs | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 15/15 | 15/15 |
| t5 | valid_server_json | 3/3 | 3/3 | 0/3 | 2/3 | 3/3 | 3/3 | 3/3 | 3/3 | 0/3 | 3/3 | 9/15 | 14/15 |
| t5 | description_le_100 | 3/3 | 3/3 | 1/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 0/3 | 3/3 | 10/15 | 15/15 |
| t5 | github_org_namespace | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 15/15 | 15/15 |
| t5 | version_matches | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 15/15 | 15/15 |
| t5 | mcpname_matches | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 15/15 | 15/15 |
| t5 | readme_read_org_token | 0/3 | 3/3 | 0/3 | 3/3 | 0/3 | 3/3 | 0/3 | 3/3 | 0/3 | 3/3 | 0/15 | 15/15 |

### What the kit-arm runs opened

| lane | kit runs | opened START-HERE | opened any story | stories opened (median) |
|---|---|---|---|---|
| haiku | 12 | 12/12 | 11/12 | 2 |
| sonnet | 12 | 12/12 | 4/12 | 0 |
| codex | 12 | 12/12 | 12/12 | 2 |
| deepseek | 12 | 12/12 | 12/12 | 3 |
| kimi | 12 | 12/12 | 12/12 | 1 |

### Did a kit run that opened the check's source story pass that check?

| check | kit runs that opened a source story: passed | kit runs that did not open it: passed | none arm: passed |
|---|---|---|---|
| t1a_output_schema_rejects_wrong | 9/11 | 1/4 | 0/15 |
| t1b_retry_no_duplicate | 12/12 | 3/3 | 15/15 |
| t1c_annotations_match | 1/1 | 14/14 | 15/15 |
| t2b_write_without_token_401 | 4/4 | 9/11 | 9/15 |
| t2a_discovery_without_token | 4/4 | 11/11 | 15/15 |
| t2c_one_consistent_rule | 4/4 | 11/11 | 15/15 |
| t3a_one_structured_line_per_call | 13/13 | 2/2 | 15/15 |
| t3b_no_personal_data_in_logs | 13/13 | 2/2 | 15/15 |
| t5a_valid_server_json | 13/14 | 1/1 | 9/15 |
| t5b_description_le_100 | 14/14 | 1/1 | 10/15 |
| t5c_github_org_namespace | 14/14 | 1/1 | 15/15 |
| t5d_version_matches | 14/14 | 1/1 | 15/15 |
| t5e_mcpname_matches | 14/14 | 1/1 | 15/15 |
| t5f_readme_read_org_token | 14/14 | 1/1 | 0/15 |

### Verdict per check (plan.md: helps = kit above none by 2+ of 3 runs in more than one lane)

| check | lanes where kit > none by 2+ | lanes where none > kit by 2+ | verdict |
|---|---|---|---|
| t1a_output_schema_rejects_wrong | codex, deepseek, kimi | - | helps |
| t1b_retry_no_duplicate | - | - | no difference |
| t1c_annotations_match | - | - | no difference |
| t2b_write_without_token_401 | codex | - | no difference |
| t2a_discovery_without_token | - | - | no difference |
| t2c_one_consistent_rule | - | - | no difference |
| t3a_one_structured_line_per_call | - | - | no difference |
| t3b_no_personal_data_in_logs | - | - | no difference |
| t5a_valid_server_json | sonnet, kimi | - | helps |
| t5b_description_le_100 | sonnet, kimi | - | helps |
| t5c_github_org_namespace | - | - | no difference |
| t5d_version_matches | - | - | no difference |
| t5e_mcpname_matches | - | - | no difference |
| t5f_readme_read_org_token | haiku, sonnet, codex, deepseek, kimi | - | helps |

Full round: 120 graded runs, 299 min of agent time.
Screening: 40 graded runs, 104 min of agent time.
