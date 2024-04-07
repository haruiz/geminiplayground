"use client";
import {BotMessageSquare, DatabaseIcon, FilesIcon, LifeBuoy, SquareUser, Triangle,} from "lucide-react"
import {Button} from "@/components/ui/button"
import {Tooltip, TooltipContent, TooltipTrigger,} from "@/components/ui/tooltip"
import {usePathname, useRouter} from 'next/navigation'
import Image from "next/image";
import {Toaster} from "@/components/ui/toaster"

function LeftTopNavBar() {

    const router = useRouter();
    const pathName = usePathname()

    const menuItems = [
        {
            icon: BotMessageSquare,
            label: "Playground",
            path: "/"
        },
        {
            icon: DatabaseIcon,
            label: "My Data",
            path: "/mydata"
        },
    ];

    const selectedItemClass = "rounded-lg bg-muted";

    return <nav className="grid gap-1 p-2">
        {menuItems.map((item, index) => (
            <Tooltip key={index}>
                <TooltipTrigger asChild>
                    <Button
                        variant="ghost"
                        size="icon"
                        className={pathName === item.path ? selectedItemClass : ""}
                        aria-label={item.label}
                        onClick={() => {
                            router.push(item.path);
                        }}
                    >
                        <item.icon className="size-5"/>
                    </Button>
                </TooltipTrigger>
                <TooltipContent side="right" sideOffset={5}>
                    {item.label}
                </TooltipContent>
            </Tooltip>
        ))}
    </nav>;
}

function AppLogo() {
    return <div className="border-b p-2 h-[60px]">
        <Button variant="outline" size="icon" aria-label="Home">
            <Triangle className="size-5 fill-foreground"/>
        </Button>
    </div>;
}

function LeftBottomNav() {
    return <nav className="mt-auto grid gap-1 p-2">
        <Tooltip>
            <TooltipTrigger asChild>
                <Button
                    variant="ghost"
                    size="icon"
                    className="mt-auto rounded-lg"
                    aria-label="Help"
                >
                    <LifeBuoy className="size-5"/>
                </Button>
            </TooltipTrigger>
            <TooltipContent side="right" sideOffset={5}>
                Help
            </TooltipContent>
        </Tooltip>
        <Tooltip>
            <TooltipTrigger asChild>
                <Button
                    variant="ghost"
                    size="icon"
                    className="mt-auto rounded-lg"
                    aria-label="Account"
                >
                    <SquareUser className="size-5"/>
                </Button>
            </TooltipTrigger>
            <TooltipContent side="right" sideOffset={5}>
                Account
            </TooltipContent>
        </Tooltip>
    </nav>;
}

function TopNavBar() {
    return <header className="sticky top-0 z-10 flex h-[60px] items-center gap-1 border-b bg-background px-4">
        <h1 className="text-xl font-semibold">Gemini Playground</h1>
        <Image src="/gemini-logo.svg" width={50} height={50} priority={true} alt={"gemini logo"}/>
    </header>;
}

export default function DefaultLayout({children}) {
    return (
        <div className="grid h-full w-full pl-[53px]">
            <aside className="inset-y fixed left-0 z-20 flex h-full flex-col border-r">
                <AppLogo/>
                <LeftTopNavBar/>
                {/*<LeftBottomNav/>*/}
            </aside>
            <TopNavBar/>
            <main className="m-2 p-2 rounded">
                {children}
            </main>
            <Toaster/>
        </div>
    )
}
