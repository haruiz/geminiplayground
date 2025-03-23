import {useQuery} from "@tanstack/react-query";
import {axiosInstance} from "@/app/axios";
import {Select, SelectContent, SelectItem, SelectTrigger, SelectValue} from "@/components/ui/select";
import {BotIcon} from "lucide-react";
import {FormControl} from "@/components/ui/form";
import {useMemo} from "react";

function beautifyNumber(number) {
    // Check if the input is a number
    if (typeof number !== 'number') {
        return "Error: Input is not a number.";
    }

    // Determine if the number is an integer or a float
    if (Number.isInteger(number)) {
        // For integers, format with thousands separators
        return number.toLocaleString();
    } else {
        // For floats, format with thousands separators and two decimal places
        return number.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2});
    }
}

export default function ModelsSelect(props) {
    const {data: modelsData = [], isLoading} = useQuery({
        queryKey: ["models"],
        queryFn: async () => {
            const {data} = await axiosInstance.get("/models");
            return data;
        },
        select: (data) =>
            data.filter(({supportedActions}) =>
                supportedActions.includes("generateContent")
            ),
    });

    const options = useMemo(() => {
        return modelsData.map(
            ({
                 name,
                 displayName,
                 description,
                 inputTokenLimit,
                 outputTokenLimit,
             }) => (
                <SelectItem key={name} value={name}>
                    <div className="flex items-start gap-3 text-muted-foreground w-[300px] p-0 m-0">
                        <BotIcon/>
                        <div className="flow flow-col gap-0.5">
                            <p className="text-sm text-foreground font-medium">{name}</p>
                            <div data-details>
                                <p className="text-xs">
                                    <span className="font-medium text-foreground">{displayName}</span>
                                </p>
                                <p className="text-xs">
                                    {description}
                                </p>
                                <p className="text-xs">
                                    <span className="font-medium text-foreground">Input tokens:</span>{' '}
                                    <span className="text-muted-foreground">{beautifyNumber(inputTokenLimit)}</span>
                                </p>
                                <p className="text-xs">
                                    <span className="font-medium text-foreground">Output tokens:</span>{' '}
                                    <span className="text-muted-foreground">{beautifyNumber(outputTokenLimit)}</span>
                                </p>
                            </div>
                        </div>
                    </div>
                </SelectItem>
            )
        );
    }, [modelsData]);

    return (
        <Select {...props}>
            <FormControl>
                <SelectTrigger
                    className="flex items-stretch [&_[data-details]]:hidden  min-w-[300px]">
                    <SelectValue
                        placeholder={isLoading ? "Loading models..." : "Select a model"}
                    />
                </SelectTrigger>
            </FormControl>
            <SelectContent>
                {isLoading ? (
                    <SelectItem disabled value="loading">
                        Loading...
                    </SelectItem>
                ) : (
                    options
                )}
            </SelectContent>
        </Select>
    );
}