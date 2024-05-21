(self.webpackChunk_N_E=self.webpackChunk_N_E||[]).push([[931],{69209:function(e,t,r){Promise.resolve().then(r.bind(r,36525))},75289:function(e,t,r){"use strict";r.d(t,{b:function(){return n}});let n=r(7908).Z.create({baseURL:"http://".concat("localhost:8081/api"),headers:{"Content-type":"application/json"}})},36525:function(e,t,r){"use strict";r.r(t),r.d(t,{default:function(){return ev}});var n=r(57437),s=r(2265);r(42162);var a=r(67153);function l(e){let{children:t}=e,[r,l]=(0,s.useState)(!1),i=a[r?"Check":"Copy"];return(0,n.jsx)("div",{className:"code-copy-btn",children:(0,n.jsx)(i,{onClick:e=>{let r=t.props.children;navigator.clipboard.writeText(r),l(!0),setTimeout(()=>{l(!1)},500)},size:18,color:r?"#0af20a":"#ddd"})})}var i=r(29676),o=r(20606),d=r(58384),c=r(78798),u=r(75707),m=r(37947),f=r(26509),p=r(6752),x=r.n(p);function g(e){let{className:t}=e;return(0,n.jsxs)("div",{className:"".concat(x().loader," ").concat(t),children:[(0,n.jsx)("span",{}),(0,n.jsx)("span",{}),(0,n.jsx)("span",{})]})}var h=r(71285),v=r(72814),j=r(86384),y=r(26355),b=r(69655),N=r(96170),w=r(193),_=r(21531),z=r(20703),k=r(67445),I=r(62177);let C=e=>{let{children:t}=e;return(0,n.jsxs)("pre",{className:"blog-pre",children:[(0,n.jsx)(l,{children:t}),t]})},R=e=>{let{markdown:t}=e;return(0,n.jsx)(h.U,{className:"markdown",remarkPlugins:[v.Z,j.Z,y.Z,b.Z],rehypePlugins:[N.Z],components:{pre:C,code(e){let{node:t,inline:r,className:s="blog-code",children:a,...l}=e,i=/language-(\w+)/.exec(s||"");return!r&&i?(0,n.jsx)(w.Z,{style:_.Z,showLineNumbers:!0,language:i[1],PreTag:"div",...l,children:String(a).replace(/\n$/,"")}):(0,n.jsx)("code",{className:s,...l,children:a})}},children:t})};function V(e){let{message:{content:t,moment:r}}=e;return(0,n.jsxs)("div",{className:"flex flex-row m-1 p-1",children:[(0,n.jsx)("div",{className:"content-center",children:(0,n.jsx)(o.Z,{className:"size-10"})}),(0,n.jsxs)("div",{className:"flex flex-col rounded-2xl bg-background fade-in ml-2 w-full p-3",children:[(0,n.jsx)("span",{className:"p-2",children:t}),(0,n.jsxs)("div",{className:"flex flex-row-re items-center gap-2 w-full place-content-end",children:[(0,n.jsx)("p",{className:"text-sm font-semibold",children:"User"}),(0,n.jsx)("p",{className:"text-xs text-muted-foreground",children:r})]})]})]})}function D(e){var t,r;let{message:{content:s,moment:a,error:l,loading:i=!1}}=e;return(0,n.jsxs)("div",{className:"flex flex-row m-1 p-1",children:[(0,n.jsxs)("div",{className:"flex flex-col rounded-2xl bg-background fade-in mr-2 w-full p-3",children:[(0,n.jsxs)("span",{className:"p-2",children:[i?(0,n.jsx)(g,{className:"absolute"}):(0,n.jsx)(R,{markdown:s}),l&&(0,n.jsx)("p",{className:"text-red-500 text-sm",children:(null==l?void 0:null===(r=l.response)||void 0===r?void 0:null===(t=r.data)||void 0===t?void 0:t.detail)||l.message})]}),(0,n.jsxs)("div",{className:"flex flex-row-re items-center gap-2 w-full place-content-end",children:[(0,n.jsx)("p",{className:"text-sm font-semibold",children:"Model"}),(0,n.jsx)("p",{className:"text-xs text-muted-foreground",children:a})]}),(0,n.jsxs)("div",{children:[(0,n.jsx)(k.z,{variant:"ghost",children:(0,n.jsx)(d.Z,{size:"15"})}),(0,n.jsx)(k.z,{variant:"ghost",children:(0,n.jsx)(c.Z,{size:"15"})}),(0,n.jsx)(k.z,{variant:"ghost",children:(0,n.jsx)(u.Z,{size:"15"})}),(0,n.jsx)(k.z,{variant:"ghost",children:(0,n.jsx)(m.Z,{size:"15"})})]})]}),(0,n.jsx)("div",{className:"content-center",children:(0,n.jsx)(f.Z,{className:"size-10"})})]})}function F(e){let{messages:t=[],onClearChatQueue:r=null}=e,s=(0,n.jsx)("div",{className:"flex flex-col items-center justify-center h-full",children:(0,n.jsx)(z.default,{src:"gemini-logo.svg",alt:"Gemini Logo",width:200,height:200,priority:!0})});if(0===t.length)return s;let a=[...t].reverse().map((e,t)=>"user"===e.role?(0,n.jsx)(V,{message:e},t):(0,n.jsx)(D,{message:e},t));return(0,n.jsxs)("div",{className:"relative pt-[40px]",children:[(0,n.jsx)(i.C,{variant:"outline",className:"absolute left-0 top-3",children:"Output"}),(0,n.jsxs)(k.z,{className:"absolute right-0 top-0",variant:"ghost",onClick:function(){console.log("Clearing chat history"),r&&r()},children:[(0,n.jsx)(I.XHJ,{})," clear"]}),a.length>0?a:s]})}var S=r(68243);let Z=s.forwardRef((e,t)=>{let{className:r,...s}=e;return(0,n.jsx)("textarea",{className:(0,S.cn)("flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50",r),ref:t,...s})});Z.displayName="Textarea",r(80763),r(29622);var T=r(85758),M=r.n(T);let P=(e,t)=>{let r=e=>"string"==typeof e?e:JSON.stringify(e);return r(e)===r(t)};function Q(e){return'\n        <tag title="'.concat(e.value,"\"\n                contenteditable='false'\n                spellcheck='false'\n                tabIndex=\"-1\"\n                class='tagify__tag  custom-tag'\n                {this.getAttributes(tagData)}>\n            <x title='' class='tagify__tag__removeBtn' role='button' aria-label='remove tag'></x>\n            <div style=\"display: flex;  align-items: center\"> \n                <div class='tagify__tag__avatar-wrap' >\n                    <img  alt=\"icon\" height=\"32px\" width=\"32px\" src=\"").concat(e.icon,"\" />\n                </div>\n                <div class='tagify__tag__info' >\n                   <span class='tagify__tag-text' style=\"margin-left: 10px\">").concat(e.name,"</span>\n                </div>\n            </div>\n        </tag>\n        ")}function E(e){return"\n        <div ".concat(this.getAttributes(e),"\n            class='tagify__dropdown__item ").concat(e.class?e.class:"",'\'\n            tabindex="0"\n            role="option">\n            ').concat(e.icon?'\n                <div class=\'tagify__dropdown__item__avatar-wrap\'>\n                    <img onerror="this.style.visibility=\'hidden\'" height="16" src="'.concat(e.icon,'">\n                </div>'):"","\n            <strong>").concat(e.name,"</strong> <br>\n            <span>").concat(e.description,"</span>\n        </div>\n    ")}let K=(0,s.forwardRef)(function(e,t){let{settings:r,whitelist:a,loading:l,readOnly:i,defaultValue:o,...d}=e,c=(0,s.useRef)(),u=(0,s.useRef)();return(0,s.useEffect)(()=>{if(!c.current||void 0===M())return;let e=new(M())(c.current,{...r,...d});return u.current=e,()=>{e.destroy(),u.current=null}},[c]),(0,s.useImperativeHandle)(t,()=>({currentValue:()=>u.current.getMixedTagsAsString(),clear:()=>{u.current.removeAllTags()}}),[u.current,c.current]),(0,s.useEffect)(()=>{u.current&&l&&u.current.loading(!0).dropdown.hide()},[l]),(0,s.useEffect)(()=>{let e=u.current;e&&o&&!l&&!P(o,e.getInputValue())&&e.loadOriginalValues('sssss [[{"value":"roses.jpg","name":"roses.jpg","description":"","icon":"http://localhost:8081/files/thumbnail_roses.jpg","type":"image","prefix":"@"}]]')},[o,l,a]),(0,s.useEffect)(()=>{let e=u.current;e&&(e.settings.whitelist.length=0,a&&a.length&&e.settings.whitelist.push(...a))},[a]),(0,s.useEffect)(()=>{let e=u.current;e&&e.setReadonly(i)},[i]),(0,n.jsx)("div",{className:"tags-input",children:(0,n.jsx)(Z,{ref:c,className:"w-full shadow-none focus-visible:ring-0"})})}),O=(0,s.forwardRef)(function(e,t){let{inputTags:r,settings:s,...a}=e;return s={maxTags:20,mode:"mix",keepInvalidTags:!0,pattern:/@/,tagTextProp:"name",pasteAsTags:!0,enforceWhitelist:!0,placeholder:"Type your message here...",dropdown:{enabled:0,classname:"chat-input",maxItems:6,mapValueTo:"name",includeSelectedTags:!0},duplicates:!0,templates:{dropdownItemNoMatch:function(e){return"<div class='".concat(this.settings.classNames.dropdownItem,'\' value="noMatch" tabindex="0" role="option">No suggestion found for: <strong>').concat(e.value,"</strong></div>")},dropdownItem:E,tag:Q},...s},(0,n.jsx)(K,{ref:t,settings:s,whitelist:r,...a})});r(56643);var q=r(86085);function J(e){let{inputTags:t=[],tagValueAccessor:r="name",onMessageSend:a=null}=e,l=(0,s.useRef)();return(0,n.jsxs)("form",{onSubmit:e=>{e.preventDefault();let t=l.current,n=t.currentValue();n&&(n=n.replace(/\[\[(.*?)\]\]/g,e=>JSON.parse(e)[0].map(e=>"["+e[r]+"]").join(", ")),a&&(a(n),t.clear()))},className:"relative rounded-lg border bg-background focus-within:ring-1 focus-within:ring-ring p-2",children:[(0,n.jsx)(O,{ref:l,inputTags:t,readOnly:!1}),(0,n.jsx)("div",{className:"flex items-center p-3 pt-0 mt-2",children:(0,n.jsxs)(k.z,{type:"submit",size:"sm",className:"ml-auto gap-1.5",children:["Send Message",(0,n.jsx)(q.Z,{className:"size-3.5"})]})})]})}var G=r(47082),A=r(94642),L=r(20568),W=r(75289),Y=r(42151),U=r.n(Y),X=r(61262),B=r(58161),H=r(23441),$=r(85159),ee=r(80037);let et=B.fC;B.ZA;let er=B.B4,en=s.forwardRef((e,t)=>{let{className:r,children:s,...a}=e;return(0,n.jsxs)(B.xz,{ref:t,className:(0,S.cn)("flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 [&>span]:line-clamp-1",r),...a,children:[s,(0,n.jsx)(B.JO,{asChild:!0,children:(0,n.jsx)(H.Z,{className:"h-4 w-4 opacity-50"})})]})});en.displayName=B.xz.displayName;let es=s.forwardRef((e,t)=>{let{className:r,...s}=e;return(0,n.jsx)(B.u_,{ref:t,className:(0,S.cn)("flex cursor-default items-center justify-center py-1",r),...s,children:(0,n.jsx)($.Z,{className:"h-4 w-4"})})});es.displayName=B.u_.displayName;let ea=s.forwardRef((e,t)=>{let{className:r,...s}=e;return(0,n.jsx)(B.$G,{ref:t,className:(0,S.cn)("flex cursor-default items-center justify-center py-1",r),...s,children:(0,n.jsx)(H.Z,{className:"h-4 w-4"})})});ea.displayName=B.$G.displayName;let el=s.forwardRef((e,t)=>{let{className:r,children:s,position:a="popper",...l}=e;return(0,n.jsx)(B.h_,{children:(0,n.jsxs)(B.VY,{ref:t,className:(0,S.cn)("relative z-50 max-h-96 min-w-[8rem] overflow-hidden rounded-md border bg-popover text-popover-foreground shadow-md data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 data-[side=bottom]:slide-in-from-top-2 data-[side=left]:slide-in-from-right-2 data-[side=right]:slide-in-from-left-2 data-[side=top]:slide-in-from-bottom-2","popper"===a&&"data-[side=bottom]:translate-y-1 data-[side=left]:-translate-x-1 data-[side=right]:translate-x-1 data-[side=top]:-translate-y-1",r),position:a,...l,children:[(0,n.jsx)(es,{}),(0,n.jsx)(B.l_,{className:(0,S.cn)("p-1","popper"===a&&"h-[var(--radix-select-trigger-height)] w-full min-w-[var(--radix-select-trigger-width)]"),children:s}),(0,n.jsx)(ea,{})]})})});el.displayName=B.VY.displayName,s.forwardRef((e,t)=>{let{className:r,...s}=e;return(0,n.jsx)(B.__,{ref:t,className:(0,S.cn)("py-1.5 pl-8 pr-2 text-sm font-semibold",r),...s})}).displayName=B.__.displayName;let ei=s.forwardRef((e,t)=>{let{className:r,children:s,...a}=e;return(0,n.jsxs)(B.ck,{ref:t,className:(0,S.cn)("relative flex w-full cursor-default select-none items-center rounded-sm py-1.5 pl-8 pr-2 text-sm outline-none focus:bg-accent focus:text-accent-foreground data-[disabled]:pointer-events-none data-[disabled]:opacity-50",r),...a,children:[(0,n.jsx)("span",{className:"absolute left-2 flex h-3.5 w-3.5 items-center justify-center",children:(0,n.jsx)(B.wU,{children:(0,n.jsx)(ee.Z,{className:"h-4 w-4"})})}),(0,n.jsx)(B.eT,{children:s})]})});ei.displayName=B.ck.displayName,s.forwardRef((e,t)=>{let{className:r,...s}=e;return(0,n.jsx)(B.Z0,{ref:t,className:(0,S.cn)("-mx-1 my-1 h-px bg-muted",r),...s})}).displayName=B.Z0.displayName;var eo=r(49006);function ed(e){return"number"!=typeof e?"Error: Input is not a number.":Number.isInteger(e)?e.toLocaleString():e.toLocaleString(void 0,{minimumFractionDigits:2,maximumFractionDigits:2})}function ec(e){let{...t}=e,{data:r,isLoading:s,refetch:a}=(0,A.a)({queryKey:["models"],queryFn:async()=>{let{data:e}=await W.b.get("/models");return e},select:e=>e.filter(e=>{let{supportedGenerationMethods:t}=e;return t.includes("generateContent")})});return(0,n.jsxs)(et,{...t,children:[(0,n.jsx)(eo.NI,{children:(0,n.jsx)(en,{className:"flex items-stretch [&_[data-description]]:hidden [&_[data-displayname]]:group-hover:flex min-w-[300px]",children:(0,n.jsx)(er,{placeholder:"Select a model"})})}),(0,n.jsx)(el,{children:null==r?void 0:r.map(e=>{let{name:t,displayName:r,description:s,inputTokenLimit:a,outputTokenLimit:l}=e;return(0,n.jsx)(ei,{value:t,children:(0,n.jsxs)("div",{className:"flex items-start gap-3 text-muted-foreground w-[300px]",children:[(0,n.jsx)(f.Z,{}),(0,n.jsxs)("div",{className:"flow flow-col gap-0.5",children:[(0,n.jsx)("p",{children:t}),(0,n.jsx)("p",{className:"text-xs","data-displayname":!0,children:(0,n.jsx)("span",{className:"font-medium text-foreground",children:r})}),(0,n.jsx)("p",{className:"text-xs","data-description":!0,children:s}),(0,n.jsxs)("p",{className:"text-xs","data-inputtokens":!0,children:[(0,n.jsx)("span",{className:"font-medium text-foreground",children:"Input tokens:"})," ",(0,n.jsx)("span",{className:"text-muted-foreground",children:ed(a)})]}),(0,n.jsxs)("p",{className:"text-xs","data-outputtokens":!0,children:[(0,n.jsx)("span",{className:"font-medium text-foreground",children:"Output tokens:"})," ",(0,n.jsx)("span",{className:"text-muted-foreground",children:ed(l)})]})]})]})},t)})})]})}var eu=r(82670),em=r(21270),ef=r(30248);let ep=ef.z.object({model:ef.z.string().min(1),temperature:ef.z.coerce.number().min(0).max(2),candidateCount:ef.z.coerce.number().int(),topP:ef.z.coerce.number().min(0).max(1),topK:ef.z.coerce.number().int()}),ex=(0,s.forwardRef)(function(e,t){let r=(0,G.NL)(),{data:a}=(0,A.a)({queryKey:["models"],queryFn:async()=>r.getQueryData(["models"])||[]}),{data:l}=(0,A.a)({queryKey:["selectedModel"],enabled:a&&a.length>0,queryFn:async()=>{var e;return r.getQueryData(["selectedModel"])||(null===(e=a[0])||void 0===e?void 0:e.name)}}),i=(0,eu.cI)({resolver:(0,em.F)(ep),defaultValues:{model:l,temperature:0,candidateCount:1,topP:.9,topK:1}});(0,s.useEffect)(()=>{l&&i.setValue("model",l,{shouldValidate:!0})},[l]);let o=async(e,t)=>{t.preventDefault(),console.log(e)};(0,s.useImperativeHandle)(t,()=>({getSettings:()=>i.getValues(),validateSettings:()=>i.trigger()}));let d=e=>{i.setValue("model",e,{shouldValidate:!0}),r.setQueryData(["selectedModel"],e);let t=r.getQueryData(["models"]);if(t){let r=t.find(t=>t.name===e);r&&(i.setValue("temperature",r.temperature,{shouldValidate:!0}),i.setValue("topP",r.topP,{shouldValidate:!0}),i.setValue("topK",r.topK,{shouldValidate:!0}))}};return(0,n.jsx)("div",{className:"w-full",children:(0,n.jsx)(eo.l0,{...i,children:(0,n.jsx)("form",{onSubmit:i.handleSubmit(o),children:(0,n.jsxs)("fieldset",{className:"grid gap-6 rounded-lg border p-4",children:[(0,n.jsx)("legend",{className:"-ml-1 px-1 text-sm font-medium",children:"Settings"}),(0,n.jsx)("div",{className:"grid gap-3",children:(0,n.jsx)(eo.Wi,{control:i.control,name:"model",render:e=>{let{field:t}=e;return(0,n.jsxs)(eo.xJ,{children:[(0,n.jsx)(eo.lX,{children:"Model"}),(0,n.jsx)(ec,{onValueChange:e=>d(e),...t}),(0,n.jsx)(eo.zG,{})]})}})}),(0,n.jsx)("div",{className:"grid gap-3",children:(0,n.jsx)(eo.Wi,{control:i.control,name:"candidateCount",render:e=>{let{field:t}=e;return(0,n.jsxs)(eo.xJ,{children:[(0,n.jsx)(eo.lX,{children:"Candidate Count"}),(0,n.jsx)(X.I,{type:"number",placeholder:0,min:0,step:.1,...t}),(0,n.jsx)(eo.zG,{})]})}})}),(0,n.jsx)("div",{className:"grid gap-3",children:(0,n.jsx)(eo.Wi,{control:i.control,name:"temperature",render:e=>{let{field:t}=e;return(0,n.jsxs)(eo.xJ,{children:[(0,n.jsx)(eo.lX,{children:"Temperature"}),(0,n.jsx)(X.I,{type:"number",placeholder:0,min:0,step:.1,...t}),(0,n.jsx)(eo.zG,{})]})}})}),(0,n.jsxs)("div",{className:"grid grid-cols-2 gap-4",children:[(0,n.jsx)("div",{className:"grid gap-3",children:(0,n.jsx)(eo.Wi,{control:i.control,name:"topP",render:e=>{let{field:t}=e;return(0,n.jsxs)(eo.xJ,{children:[(0,n.jsx)(eo.lX,{children:"Top P"}),(0,n.jsx)(X.I,{type:"number",placeholder:0,step:.1,...t}),(0,n.jsx)(eo.zG,{})]})}})}),(0,n.jsx)("div",{className:"grid gap-3",children:(0,n.jsx)(eo.Wi,{control:i.control,name:"topK",render:e=>{let{field:t}=e;return(0,n.jsxs)(eo.xJ,{children:[(0,n.jsx)(eo.lX,{children:"Top K"}),(0,n.jsx)(X.I,{type:"number",placeholder:0,min:0,step:1,...t}),(0,n.jsx)(eo.zG,{})]})}})})]})]})})})})});var eg=r(4617);let eh="ws://".concat("localhost:8081/api","/ws");function ev(){let e=(0,G.NL)(),t=(0,s.useRef)(null),{sendJsonMessage:r,lastJsonMessage:a,readyState:l}=(0,eg.ZP)(eh,{share:!1,shouldReconnect:()=>!0});(0,s.useEffect)(()=>{console.log("Connection state changed"),l===eg.kQ.OPEN&&r({event:"subscribe",data:{channel:"messages"}})},[r,l]);let i="/tags",{data:o,isLoading:d,refetch:c}=(0,A.a)({queryKey:[i],queryFn:async()=>(await W.b.get(i)).data}),{data:u}=(0,A.a)({queryKey:["messages"],queryFn:async()=>e.getQueryData(["messages"])||[]}),m=(0,L.D)({mutationFn:async e=>{r({event:"generate_response",data:e})}});(0,s.useEffect)(()=>{let{event:e,data:t}=a||{};if("response_completed"===e)p.mutate({loading:!1});else if("response_chunk"===e){let e=x();if(e){let{content:r}=e;p.mutate({content:r+t,loading:!1})}}else"response_error"===e&&p.mutate({content:"Ups! Something went wrong. I cannot generate a response at the moment",loading:!1,error:t})},[a]);let f=(0,L.D)({mutationFn:async t=>{e.setQueryData(["messages"],e=>[...e,t])}});(0,L.D)({mutationFn:async t=>{e.setQueryData(["messages"],e=>e.map(e=>e.timestamp===t.timestamp?t:e))}});let p=(0,L.D)({mutationFn:async t=>{e.setQueryData(["messages"],e=>{let r={...e[e.length-1],...t};return[...e.slice(0,-1),r]})}}),x=()=>e.getQueryData(["messages"])[e.getQueryData(["messages"]).length-1];function g(e,t,r,n){let s=arguments.length>4&&void 0!==arguments[4]?arguments[4]:null,a={role:e,content:t,timestamp:new Date().toISOString(),rawMessage:n,loading:r,moment:U()().format("MMMM Do YYYY, h:mm:ss a")};s&&(a.error=s),f.mutate(a)}async function h(r){if(r)try{let n=t.current;if(!await n.validateSettings())return;let s=e.getQueryData(["selectedModel"]),a=t.current.getSettings();a={temperature:parseFloat(a.temperature),candidateCount:parseInt(a.candidateCount),topK:parseInt(a.topK),topP:parseFloat(a.topP)};let l={model:s,message:r,settings:a};g("user",r.replace(/[\[\](){}<>]/g,""),!1,r),g("model","",!0,r),await m.mutateAsync(l)}catch(e){console.log("error in generating response",e),p.mutate({content:"Ups! Something went wrong. I cannot generate a response at the moment",loading:!1,error:e})}}let v=async(e,t)=>{await h(e)},j=async()=>{e.setQueryData(["messages"],[]),r({event:"clear_queue",data:{}})};return(0,n.jsxs)("div",{className:"flex flex-col lg:flex-row gap-3",children:[(0,n.jsx)("div",{className:"w-full",children:(0,n.jsxs)("div",{className:"flex flex-col  rounded-xl bg-muted/50 p-1 border-2 h-screen lg:h-[calc(100vh-90px)] w-full m-0",children:[(0,n.jsx)("div",{className:"w-full h-dvh overflow-auto",children:(0,n.jsx)(F,{messages:u,onClearChatQueue:j})}),(0,n.jsx)("div",{className:"w-full",children:(0,n.jsx)(J,{inputTags:o,onMessageSend:v,tagValueAccessor:"name"})})]})}),(0,n.jsx)("div",{children:(0,n.jsx)(ex,{ref:t})})]})}},29676:function(e,t,r){"use strict";r.d(t,{C:function(){return i}});var n=r(57437);r(2265);var s=r(57742),a=r(68243);let l=(0,s.j)("inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",{variants:{variant:{default:"border-transparent bg-primary text-primary-foreground hover:bg-primary/80",secondary:"border-transparent bg-secondary text-secondary-foreground hover:bg-secondary/80",destructive:"border-transparent bg-destructive text-destructive-foreground hover:bg-destructive/80",outline:"text-foreground"}},defaultVariants:{variant:"default"}});function i(e){let{className:t,variant:r,...s}=e;return(0,n.jsx)("div",{className:(0,a.cn)(l({variant:r}),t),...s})}},67445:function(e,t,r){"use strict";r.d(t,{d:function(){return o},z:function(){return d}});var n=r(57437),s=r(2265),a=r(59143),l=r(57742),i=r(68243);let o=(0,l.j)("inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50",{variants:{variant:{default:"bg-primary text-primary-foreground hover:bg-primary/90",destructive:"bg-destructive text-destructive-foreground hover:bg-destructive/90",outline:"border border-input bg-background hover:bg-accent hover:text-accent-foreground",secondary:"bg-secondary text-secondary-foreground hover:bg-secondary/80",ghost:"hover:bg-accent hover:text-accent-foreground",link:"text-primary underline-offset-4 hover:underline"},size:{default:"h-10 px-4 py-2",sm:"h-9 rounded-md px-3",lg:"h-11 rounded-md px-8",icon:"h-10 w-10"}},defaultVariants:{variant:"default",size:"default"}}),d=s.forwardRef((e,t)=>{let{className:r,variant:s,size:l,asChild:d=!1,...c}=e,u=d?a.g7:"button";return(0,n.jsx)(u,{className:(0,i.cn)(o({variant:s,size:l,className:r})),ref:t,...c})});d.displayName="Button"},49006:function(e,t,r){"use strict";r.d(t,{l0:function(){return u},NI:function(){return v},pf:function(){return j},Wi:function(){return f},xJ:function(){return g},lX:function(){return h},zG:function(){return y}});var n=r(57437),s=r(2265),a=r(59143),l=r(82670),i=r(68243),o=r(24602);let d=(0,r(57742).j)("text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"),c=s.forwardRef((e,t)=>{let{className:r,...s}=e;return(0,n.jsx)(o.f,{ref:t,className:(0,i.cn)(d(),r),...s})});c.displayName=o.f.displayName;let u=l.RV,m=s.createContext({}),f=e=>{let{...t}=e;return(0,n.jsx)(m.Provider,{value:{name:t.name},children:(0,n.jsx)(l.Qr,{...t})})},p=()=>{let e=s.useContext(m),t=s.useContext(x),{getFieldState:r,formState:n}=(0,l.Gc)(),a=r(e.name,n);if(!e)throw Error("useFormField should be used within <FormField>");let{id:i}=t;return{id:i,name:e.name,formItemId:"".concat(i,"-form-item"),formDescriptionId:"".concat(i,"-form-item-description"),formMessageId:"".concat(i,"-form-item-message"),...a}},x=s.createContext({}),g=s.forwardRef((e,t)=>{let{className:r,...a}=e,l=s.useId();return(0,n.jsx)(x.Provider,{value:{id:l},children:(0,n.jsx)("div",{ref:t,className:(0,i.cn)("space-y-2",r),...a})})});g.displayName="FormItem";let h=s.forwardRef((e,t)=>{let{className:r,...s}=e,{error:a,formItemId:l}=p();return(0,n.jsx)(c,{ref:t,className:(0,i.cn)(a&&"text-destructive",r),htmlFor:l,...s})});h.displayName="FormLabel";let v=s.forwardRef((e,t)=>{let{...r}=e,{error:s,formItemId:l,formDescriptionId:i,formMessageId:o}=p();return(0,n.jsx)(a.g7,{ref:t,id:l,"aria-describedby":s?"".concat(i," ").concat(o):"".concat(i),"aria-invalid":!!s,...r})});v.displayName="FormControl";let j=s.forwardRef((e,t)=>{let{className:r,...s}=e,{formDescriptionId:a}=p();return(0,n.jsx)("p",{ref:t,id:a,className:(0,i.cn)("text-sm text-muted-foreground",r),...s})});j.displayName="FormDescription";let y=s.forwardRef((e,t)=>{let{className:r,children:s,...a}=e,{error:l,formMessageId:o}=p(),d=l?String(null==l?void 0:l.message):s;return d?(0,n.jsx)("p",{ref:t,id:o,className:(0,i.cn)("text-sm font-medium text-destructive",r),...a,children:d}):null});y.displayName="FormMessage"},61262:function(e,t,r){"use strict";r.d(t,{I:function(){return l}});var n=r(57437),s=r(2265),a=r(68243);let l=s.forwardRef((e,t)=>{let{className:r,type:s,...l}=e;return(0,n.jsx)("input",{type:s,className:(0,a.cn)("flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50",r),ref:t,...l})});l.displayName="Input"},56643:function(e,t,r){"use strict";r.d(t,{_v:function(){return c},aJ:function(){return d},pn:function(){return i},u:function(){return o}});var n=r(57437),s=r(2265),a=r(38152),l=r(68243);let i=a.zt,o=a.fC,d=a.xz,c=s.forwardRef((e,t)=>{let{className:r,sideOffset:s=4,...i}=e;return(0,n.jsx)(a.VY,{ref:t,sideOffset:s,className:(0,l.cn)("z-50 overflow-hidden rounded-md border bg-popover px-3 py-1.5 text-sm text-popover-foreground shadow-md animate-in fade-in-0 zoom-in-95 data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=closed]:zoom-out-95 data-[side=bottom]:slide-in-from-top-2 data-[side=left]:slide-in-from-right-2 data-[side=right]:slide-in-from-left-2 data-[side=top]:slide-in-from-bottom-2",r),...i})});c.displayName=a.VY.displayName},68243:function(e,t,r){"use strict";r.d(t,{cn:function(){return a}});var n=r(75504),s=r(51367);function a(){for(var e=arguments.length,t=Array(e),r=0;r<e;r++)t[r]=arguments[r];return(0,s.m6)((0,n.W)(t))}},29622:function(){},42162:function(){},6752:function(e){e.exports={loader:"styles_loader__bURed"}}},function(e){e.O(0,[310,990,217,96,99,317,971,69,744],function(){return e(e.s=69209)}),_N_E=e.O()}]);
