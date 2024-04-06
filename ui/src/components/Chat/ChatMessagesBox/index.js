import CodeCopyBtn from "@/components/CodeCopyButton";
import {Badge} from "@/components/ui/badge";
import {BotIcon, ClipboardCopy, CopyIcon, Facebook, RefreshCcw, ThumbsDown, ThumbsUp, UserCircle2} from "lucide-react";
import Spinner from "@/components/Spinner/Spinner";
import Markdown from "react-markdown";
import remarkParse from "remark-parse";
import remarkGfm from "remark-gfm";
import remarkRehype from "remark-rehype";
import rehypeStringify from "rehype-stringify";
import rehypeRaw from "rehype-raw";
import {Prism as SyntaxHighlighter} from "react-syntax-highlighter";
import {oneDark as primTheme} from "react-syntax-highlighter/src/styles/prism";
import Image from "next/image";
import {Button} from "@/components/ui/button";
import {TrashIcon} from "@radix-ui/react-icons";

export const Pre = ({children}) => <pre className="blog-pre">
        <CodeCopyBtn>{children}</CodeCopyBtn>
    {children}
    </pre>

const OutputMessage = ({markdown}) => {
    return <Markdown
        className="markdown"
        remarkPlugins={[remarkParse, remarkGfm, remarkRehype, rehypeStringify]}
        rehypePlugins={[rehypeRaw]}
        components={{
            pre: Pre,
            code({node, inline, className = "blog-code", children, ...props}) {
                const match = /language-(\w+)/.exec(className || '')
                return !inline && match ? (
                    <SyntaxHighlighter
                        style={primTheme}
                        showLineNumbers
                        language={match[1]}
                        PreTag="div"
                        {...props}
                    >
                        {String(children).replace(/\n$/, '')}
                    </SyntaxHighlighter>
                ) : (
                    <code className={className} {...props}>
                        {children}
                    </code>
                )
            }
        }}
    >
        {markdown}
    </Markdown>
}


function UserMessage({message: {content, moment}}) {
    return <div className="flex flex-row m-1 p-1">
        <div className="content-center">
            <UserCircle2 className={"size-10"}/>
        </div>
        <div className="flex flex-col rounded-2xl bg-background fade-in ml-2 w-full p-3">
            <span className="p-2">{content}</span>
            <div className="flex flex-row-re items-center gap-2 w-full place-content-end">
                <p className="text-sm font-semibold">User</p>
                <p className="text-xs text-muted-foreground">{moment}</p>
            </div>
        </div>
    </div>;
}

function ModelMessage({message: {content, moment, error, loading = false}}) {
    return <div className="flex flex-row m-1 p-1">
        <div className="flex flex-col rounded-2xl bg-background fade-in mr-2 w-full p-3">
            <span className="p-2">
                {loading ? <Spinner className="absolute"/> : <OutputMessage markdown={content}/>}
                {error && <p className="text-red-500 text-sm">{error?.response?.data?.detail || error.message}</p>}
            </span>
            <div className="flex flex-row-re items-center gap-2 w-full place-content-end">
                <p className="text-sm font-semibold">Model</p>
                <p className="text-xs text-muted-foreground">{moment}</p>
            </div>
            <div>
                <Button variant="ghost">
                    <ClipboardCopy size="15"/>
                </Button>
                <Button variant="ghost">
                    <RefreshCcw size="15"/>
                </Button>
                <Button variant="ghost">
                    <ThumbsUp size="15"/>
                </Button>
                <Button variant="ghost">
                    <ThumbsDown size="15"/>
                </Button>
            </div>
        </div>
        <div className="content-center">
            <BotIcon className="size-10"/>
        </div>
    </div>;
}

export default function ChatMessagesBox({messages = [], onClearChatQueue = null}) {

    const emptyMessageQueueContent = <div className="flex flex-col items-center justify-center h-full">
        <Image src="gemini-logo.svg" alt="Gemini Logo" width={200} height={200} priority={true}/>
    </div>
    if (messages.length === 0) {
        return emptyMessageQueueContent;
    }

    const messageQueueContent = [...messages].reverse().map((message, index) => {
        if (message.role === "user") {
            return <UserMessage key={index} message={message}/>
        } else {
            return <ModelMessage key={index} message={message}/>
        }
    });

    function clearHistory() {
        console.log("Clearing chat history");
        if (onClearChatQueue) {
            onClearChatQueue();
        }
    }

    return (
        <div className="relative pt-[40px]">
            <Badge variant="outline" className="absolute left-0 top-3">
                Output
            </Badge>
            <Button className="absolute right-0 top-0" variant="ghost" onClick={clearHistory}>
                <TrashIcon/> clear
            </Button>
            {messageQueueContent.length > 0 ? messageQueueContent : emptyMessageQueueContent}
        </div>
    )
}

