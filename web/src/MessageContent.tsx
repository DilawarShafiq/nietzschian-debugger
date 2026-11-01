import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";

export function MessageContent({ content }: { content: string }) {
  return <div className="message-content">
    <Markdown remarkPlugins={[remarkGfm]} skipHtml components={{
      // Avoid remote tracking images embedded in model output.
      img: ({ alt }) => <span>{alt}</span>,
      a: ({ children, href }) => <a href={href} target="_blank" rel="noopener noreferrer" referrerPolicy="no-referrer">{children}</a>,
    }}>{content}</Markdown>
  </div>;
}
