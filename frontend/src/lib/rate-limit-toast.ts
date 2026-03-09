import { toast } from "sonner";

let activeToastId: string | number | undefined;

/**
 * Handles HTTP 429 responses by showing a toast notification with countdown.
 * Returns true if the response was a 429, false otherwise.
 */
export function handleRateLimitResponse(res: Response): boolean {
  if (res.status !== 429) return false;

  const retryAfterHeader = res.headers.get("Retry-After");
  const retryAfterSeconds = retryAfterHeader ? parseInt(retryAfterHeader, 10) : null;
  const dismissAfter = retryAfterSeconds
    ? Math.min(retryAfterSeconds, 10) * 1000
    : 10000;

  const message = retryAfterSeconds
    ? `You're making requests too quickly. Please wait ${retryAfterSeconds} seconds and try again.`
    : "You're making requests too quickly. Please wait a moment and try again.";

  // Dismiss previous rate limit toast to avoid stacking
  if (activeToastId !== undefined) {
    toast.dismiss(activeToastId);
  }

  activeToastId = toast.warning(message, {
    duration: dismissAfter,
    id: "rate-limit-429",
    onDismiss: () => { activeToastId = undefined; },
    onAutoClose: () => { activeToastId = undefined; },
  });

  return true;
}
