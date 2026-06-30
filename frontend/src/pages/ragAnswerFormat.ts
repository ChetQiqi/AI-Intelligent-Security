export type RAGAnswerBlock =
  | { type: 'heading'; content: string }
  | { type: 'paragraph'; content: string }
  | { type: 'ordered-item'; content: string }
  | { type: 'unordered-item'; content: string };

export function parseRAGAnswer(answer: string): RAGAnswerBlock[] {
  return answer
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean)
    .map((line) => {
      const heading = line.match(/^#{1,3}\s+(.+)$/);
      if (heading) {
        return { type: 'heading', content: heading[1].trim() };
      }

      const ordered = line.match(/^\d+[.)、]\s*(.+)$/);
      if (ordered) {
        return { type: 'ordered-item', content: ordered[1].trim() };
      }

      const unordered = line.match(/^[-*]\s*(.+)$/);
      if (unordered) {
        return { type: 'unordered-item', content: unordered[1].trim() };
      }

      return { type: 'paragraph', content: line };
    });
}
