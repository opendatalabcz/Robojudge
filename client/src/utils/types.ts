export type Case = {
  rulingId: string;
  summary: string;
  title: string;
  metadata: Record<string, unknown>;
  reasoning: string;
  verdict: string;
  isLoading: boolean;
};
