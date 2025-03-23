"use client";
import {Button} from "@/components/ui/button"
import {FileIcon, GitHubLogoIcon, PlusIcon, TrashIcon} from "@radix-ui/react-icons"
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import {forwardRef, useImperativeHandle, useRef, useState} from "react";
import FileUploadForm from "@/app/mydata/FileUploadForm";
import CodeRepoForm from "@/app/mydata/CodeRepoForm";
import {useMutation, useQuery, useQueryClient} from "@tanstack/react-query";
import {Loader2, MoreHorizontal, SeparatorHorizontal} from "lucide-react";
import {axiosInstance} from "@/app/axios";
import DataTable from "@/components/DataTable";
import ConfirmDialog from "@/components/ConfirmDialog";
import {Badge} from "@/components/ui/badge"
import {
    Tooltip,
    TooltipContent,
    TooltipProvider,
    TooltipTrigger,
} from "@/components/ui/tooltip"
import Image from "next/image";


export function ButtonLoading({loading, children, ...rest}) {
    return (
        <Button disabled={loading} {...rest}>
            {loading && (
                <Loader2 className="animate-spin mr-2 h-4 w-4"/>
            )}
            {loading ? "Please wait..." : children}
        </Button>
    );
}


const FilesTable = forwardRef(function FilesTable({...rest}, ref) {
    const filesUrl = `http://${process.env.NEXT_PUBLIC_API_BASE_URL}/files`;
    const confirmDialogRef = useRef();
    const queryClient = useQueryClient()

    const {data, isLoading, refetch} = useQuery({
        queryKey: ["parts"],
        refetchInterval: 10000,
        queryFn: async () => {
            const response = await axiosInstance.get("/parts")
            return response.data
        }
    })

    const deleteFileMutation = useMutation({
        mutationFn: async (name) => {
            await axiosInstance.delete(`/parts/${name}`);
        }
    })


    const refresh = async () => {
        await queryClient.invalidateQueries({queryKey: ["parts"]});
        await refetch();
    }

    useImperativeHandle(ref, () => ({
        refresh
    }), []);


    const filesTableColumns = [
        {
            header: "Image",
            width: 80,
            cell: ({row}) => {
                const data = row.original
                const {thumbnail, status} = data
                const imageUrl = status === "ready" ? `${filesUrl}/${thumbnail}` : "https://placehold.co/50x50"
                return (
                    <div className="flex items-center space-x-2">
                        <Image src={imageUrl} width={50} height={50} alt={data.name}/>
                    </div>
                )
            }
        },
        {
            header: "Name",
            accessorKey: "name",
        },
        {
            header: "Type",
            accessorKey: "type",
        },
        {
            header: "Status",
            cell: ({row}) => {
                const status = row.original.status
                const statusMessage = row.original.statusMessage
                if (status === "ready" || status === "pending") {
                    return <Badge variant="secondary">{status}</Badge>
                }
                return (
                    <TooltipProvider>
                        <Tooltip>
                            <TooltipTrigger>
                                <Badge variant="destructive"
                                       style={{cursor: "pointer"}}>{status}</Badge>
                            </TooltipTrigger>
                            <TooltipContent>
                                <p>{statusMessage}</p>
                            </TooltipContent>
                        </Tooltip>
                    </TooltipProvider>
                )
            }
        },
        {
            header: "Actions",
            cell: ({row}) => {
                const data = row.original
                return (
                    <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                            <Button variant="ghost" className="h-8 w-8 p-0">
                                <span className="sr-only">Open menu</span>
                                <MoreHorizontal className="h-4 w-4"/>
                            </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                            <DropdownMenuLabel>Actions</DropdownMenuLabel>
                            <DropdownMenuItem
                                onClick={() => {
                                    const dialog = confirmDialogRef.current
                                    if (dialog) {
                                        dialog.open(
                                            "Delete",
                                            "Are you sure you want to delete this file?",
                                            async (result) => {
                                                if (result) {
                                                    await deleteFileMutation.mutateAsync(data.name);
                                                    await queryClient.refetchQueries(["parts"])
                                                }
                                            }
                                        )
                                    }
                                }}
                            >
                                <TrashIcon className="mr-2 h-4 w-4"/> Delete
                            </DropdownMenuItem>
                            {/*<DropdownMenuSeparator/>*/}
                        </DropdownMenuContent>
                    </DropdownMenu>
                )
            }
        }
    ];
    const filesTableData = data ? data.map((item) => {
        return {
            name: item.name,
            type: item.content_type,
            status: item.status,
            statusMessage: item.status_message,
            thumbnail: item.thumbnail
        }
    }) : []
    return (
        <>
            <ConfirmDialog ref={confirmDialogRef}/>
            <DataTable columns={filesTableColumns} data={filesTableData} className="w-full"/>
        </>
    );
});


export default function FilesPage() {

    const uploadFileFormRef = useRef();
    const codeRepoFormRef = useRef();
    const fileTableRef = useRef();
    const [deletingAllFiles, setDeletingAllFiles] = useState(false);
    const queryClient = useQueryClient();


    const deleteAllMutation = useMutation({
        mutationFn: async () => {
            return axiosInstance.delete(`/deleteAllFiles`);
        },
        onSuccess: async () => {
            await queryClient.refetchQueries(["parts"])
        }
    })

    const newFileHandler = () => {
        const form = uploadFileFormRef.current;
        if (form) {
            form.reset();
            form.open();
        }
    }
    const newCodeRepoHandler = () => {
        const form = codeRepoFormRef.current;
        if (form) {
            form.reset();
            form.open();
        }
    }


    const handleDeleteAll = async () => {
        setDeletingAllFiles(true);
        const response = await deleteAllMutation.mutateAsync();
        console.log("Delete All Response", response);
        setDeletingAllFiles(false);
    }

    return (
        <>
            <header className="w-full p-2">
                <h1 className="text-xl font-semibold">Files</h1>
            </header>
            <main>
                <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                        <Button>
                            <PlusIcon className="mr-2 h-4 w-4"/> Upload Data
                        </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent className="w-56">
                        <DropdownMenuItem onSelect={newFileHandler}> <FileIcon
                            className="mr-2 h-4 w-4"/>Upload File</DropdownMenuItem>
                        <DropdownMenuItem onSelect={newCodeRepoHandler}> <GitHubLogoIcon
                            className="mr-2 h-4 w-4"/> Code
                            repository</DropdownMenuItem>
                    </DropdownMenuContent>
                </DropdownMenu>
                <ButtonLoading className="ml-2" loading={deletingAllFiles} onClick={handleDeleteAll}>
                    <TrashIcon className="mr-2 h-4 w-4"/> Delete Data
                </ButtonLoading>
                <div className="rounded-md border m-3">
                    <FilesTable ref={fileTableRef}/>
                </div>
            </main>

            <FileUploadForm ref={uploadFileFormRef}/>
            <CodeRepoForm ref={codeRepoFormRef}/>
        </>
    );
}
