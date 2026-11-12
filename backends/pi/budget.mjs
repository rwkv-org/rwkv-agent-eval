// Turn budget for one Pi run (one user turn), without touching the prompt.
//
// Harbor's stock Pi max_turns extension appends "You have a hard budget of N
// model turns..." to the system prompt. RWKV was trained on rwkv-pi harness
// prompts without that sentence, so this extension only counts completed model
// turns and aborts at the limit: the prompt stays byte-identical to training.
//
//   RAE_MAX_TURNS=<n>   0 or unset: no limit
export default function raeTurnBudget(pi) {
  const max = Number.parseInt(process.env.RAE_MAX_TURNS || '0', 10);
  if (!Number.isSafeInteger(max) || max <= 0) return;
  let done = 0;
  pi.on('turn_end', (_event, ctx) => {
    done += 1;
    if (done >= max) ctx.abort();
  });
}
