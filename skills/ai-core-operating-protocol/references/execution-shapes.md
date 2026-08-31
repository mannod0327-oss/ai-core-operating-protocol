# Execution Shapes

Choose the least autonomous shape that can reliably complete the task.

- **Direct:** stable, self-contained work with no meaningful multi-step dependency.
- **Deterministic workflow:** the route is known in advance; use explicit stages and validation.
- **Parallel workers:** only for genuinely independent units without shared mutable state or sequential dependency.
- **Orchestrator-worker:** decompose a large task, execute independent units, synthesize once, then evaluate.
- **Agentic loop:** only when the next useful action depends on observations from the previous action.

Avoid agent-count theater, parallelizing dependent steps, repeated failed actions without a changed hypothesis, and planning that prevents execution.

Parallel/subagent execution additionally requires host and task permission; this skill does not override a no-delegation rule. Give each worker a bounded task and separate writes. Two unchanged failed attempts should trigger a new hypothesis or a blocker report, not an endless retry loop.
