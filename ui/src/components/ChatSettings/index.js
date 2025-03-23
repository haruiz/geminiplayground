"use client";
import {Input} from "@/components/ui/input";
import {useQuery, useQueryClient} from "@tanstack/react-query";
import ModelsSelect from "@/components/ModelsSelect";
import {Form, FormField, FormItem, FormLabel, FormMessage,} from "@/components/ui/form"
import {useForm} from "react-hook-form"
import {zodResolver} from "@hookform/resolvers/zod";
import {z} from "zod"
import {forwardRef, useEffect, useImperativeHandle} from "react";

const FormSchema = z.object({
    model: z.string().min(1, {
        message: "Model is required"
    }),
    temperature: z.coerce.number().min(0.0).max(2.0),
    // candidateCount: z.coerce.number().int(),
    topP: z.coerce.number().min(0.0).max(1.0),
    topK: z.coerce.number().int()
})

const ChatSettings = forwardRef(function ChatSettings(props, ref) {

    const queryClient = useQueryClient();

    const {data: settingsData, isLoading} = useQuery({
        queryKey: ["settings"],
        queryFn: async () => {
            return queryClient.getQueryData(["settings"]) || null;
        },
    });

    const form = useForm({
        resolver: zodResolver(FormSchema),
        defaultValues: {
            model: settingsData?.model || "",
            temperature: settingsData?.temperature || 1.0,
            topP: settingsData?.topP || 0.95,
            topK: settingsData?.topK || 0
        }
    });
    const allFields = form.watch();
    useEffect(() => {
        queryClient.setQueryData(["settings"], allFields);
    }, [allFields]);

    const onSubmit = async (data, evt) => {
        evt.preventDefault();
        console.log(data);

    };

    useImperativeHandle(ref, () => ({
        getSettings: () => form.getValues(),
        validateSettings: () => form.trigger(),
    }));

    return <div className="w-full">
        <Form {...form} >
            <form onSubmit={form.handleSubmit(onSubmit)}>
                <fieldset className="grid gap-6 rounded-lg border p-4">
                    <legend className="-ml-1 px-1 text-sm font-medium">
                        Settings
                    </legend>
                    <div className="grid gap-3">
                        <FormField
                            control={form.control}
                            name="model"
                            render={({field}) => (
                                <FormItem>
                                    <FormLabel>Model</FormLabel>
                                    <ModelsSelect
                                        {...field}
                                        onValueChange={(value) => {
                                            form.setValue("model", value, {shouldValidate: true})
                                        }}/>
                                    <FormMessage/>
                                </FormItem>
                            )}
                        />
                    </div>
                    <div className="grid gap-3">
                        <FormField
                            control={form.control}
                            name="temperature"
                            render={({field}) => (
                                <FormItem>
                                    <FormLabel>Temperature</FormLabel>
                                    <Input type="number"
                                           placeholder={0.0}
                                           min={0.0} step={0.1}

                                           {...field}/>
                                    <FormMessage/>
                                </FormItem>
                            )}
                        />
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                        <div className="grid gap-3">
                            <FormField
                                control={form.control}
                                name="topP"
                                render={({field}) => (
                                    <FormItem>
                                        <FormLabel>Top P</FormLabel>
                                        <Input type="number"
                                               placeholder={0.0}
                                               step={0.1}
                                               {...field}/>
                                        <FormMessage/>
                                    </FormItem>
                                )}
                            />
                        </div>
                        <div className="grid gap-3">
                            <FormField
                                control={form.control}
                                name="topK"
                                render={({field}) => (
                                    <FormItem>
                                        <FormLabel>Top K</FormLabel>
                                        <Input type="number"
                                               placeholder={0.0}
                                               min={0.0} step={1}
                                               {...field}/>
                                        <FormMessage/>
                                    </FormItem>
                                )}
                            />
                        </div>
                    </div>
                </fieldset>
            </form>
        </Form>
    </div>;
});

export default ChatSettings;