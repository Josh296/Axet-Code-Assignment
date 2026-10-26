# Project Instructions

- Implement LogScope in Python using only the standard library unless a dependency is justified in the plan.
- Keep log processing streaming: iterate files line by line and avoid retaining raw input lines except where command output requires them.
- Treat malformed log lines as non-fatal: count them and continue processing.
- Add focused unit tests for every feature before proceeding to the next implementation stage.
- Run the relevant test suite after each change.
- Do not create commits. Before any manual update to project files after planning, request the user's permission.
- Keep generated benchmark logs and benchmark artifacts out of version control.
