import{_ as n}from"./TUMLogo.vue_vue_type_script_setup_true_lang-DZ3tKll7.js";import{_ as p}from"./slidev/CodeBlockWrapper.vue_vue_type_script_setup_true_lang-njK8816k.js";import{o,c as d,k as a,l as t,m as g,q as c,s as y,A as h,e as s,a6 as i}from"./modules/vue-C7iSKaD9.js";import{I as m}from"./slidev/two-cols-header-BMTXqsuo.js";import{ag as k}from"./index-BfB8TzU9.js";import{p as E,u as A,f as D}from"./slidev/context-CWakdmAW.js";import"./modules/unplugin-icons-CquepfLA.js";import"./modules/shiki-BlbLwIsd.js";const _="/assets/WorkerSM-DRZ8lKz9.png",f=s("h1",null,"Worker State Machine",-1),C=s("ul",null,[s("li",null,"Workers are reply sockets"),s("li",null,[i("Bind and block on "),s("code",null,"recv()")]),s("li",null,"Process message based on type")],-1),B=s("pre",{class:"shiki shiki-themes vitesse-dark vitesse-light slidev-code",style:{"--shiki-dark":"#dbd7caee","--shiki-light":"#393a34","--shiki-dark-bg":"#121212","--shiki-light-bg":"#ffffff"}},[s("code",{class:"language-python"},[s("span",{class:"line"},[s("span",{style:{"--shiki-dark":"#4D9375","--shiki-light":"#1E754F"}},"while"),s("span",{style:{"--shiki-dark":"#666666","--shiki-light":"#999999"}},"("),s("span",{style:{"--shiki-dark":"#4D9375","--shiki-light":"#1E754F"}},"True"),s("span",{style:{"--shiki-dark":"#666666","--shiki-light":"#999999"}},"):")]),i(`
`),s("span",{class:"line"},[s("span",{style:{"--shiki-dark":"#DBD7CAEE","--shiki-light":"#393A34"}},"    m "),s("span",{style:{"--shiki-dark":"#666666","--shiki-light":"#999999"}},"="),s("span",{style:{"--shiki-dark":"#C99076","--shiki-light":"#A65E2B"}}," self"),s("span",{style:{"--shiki-dark":"#666666","--shiki-light":"#999999"}},"."),s("span",{style:{"--shiki-dark":"#DBD7CAEE","--shiki-light":"#393A34"}},"recv_message"),s("span",{style:{"--shiki-dark":"#666666","--shiki-light":"#999999"}},"()")]),i(`
`),s("span",{class:"line"},[s("span",{style:{"--shiki-dark":"#4D9375","--shiki-light":"#1E754F"}},"    match"),s("span",{style:{"--shiki-dark":"#DBD7CAEE","--shiki-light":"#393A34"}}," m"),s("span",{style:{"--shiki-dark":"#666666","--shiki-light":"#999999"}},"."),s("span",{style:{"--shiki-dark":"#DBD7CAEE","--shiki-light":"#393A34"}},"type"),s("span",{style:{"--shiki-dark":"#666666","--shiki-light":"#999999"}},":")]),i(`
`),s("span",{class:"line"},[s("span",{style:{"--shiki-dark":"#4D9375","--shiki-light":"#1E754F"}},"        case"),s("span",{style:{"--shiki-dark":"#C99076","--shiki-light":"#A65E2B"}}," CONNECT"),s("span",{style:{"--shiki-dark":"#666666","--shiki-light":"#999999"}},":"),s("span",{style:{"--shiki-dark":"#C99076","--shiki-light":"#A65E2B"}}," self"),s("span",{style:{"--shiki-dark":"#666666","--shiki-light":"#999999"}},"."),s("span",{style:{"--shiki-dark":"#DBD7CAEE","--shiki-light":"#393A34"}},"connectACK"),s("span",{style:{"--shiki-dark":"#666666","--shiki-light":"#999999"}},"("),s("span",{style:{"--shiki-dark":"#DBD7CAEE","--shiki-light":"#393A34"}},"m"),s("span",{style:{"--shiki-dark":"#666666","--shiki-light":"#999999"}},")")]),i(`
`),s("span",{class:"line"},[s("span",{style:{"--shiki-dark":"#4D9375","--shiki-light":"#1E754F"}},"        case"),s("span",{style:{"--shiki-dark":"#C99076","--shiki-light":"#A65E2B"}}," COMMAND"),s("span",{style:{"--shiki-dark":"#666666","--shiki-light":"#999999"}},":"),s("span",{style:{"--shiki-dark":"#C99076","--shiki-light":"#A65E2B"}}," self"),s("span",{style:{"--shiki-dark":"#666666","--shiki-light":"#999999"}},"."),s("span",{style:{"--shiki-dark":"#DBD7CAEE","--shiki-light":"#393A34"}},"commandACK"),s("span",{style:{"--shiki-dark":"#666666","--shiki-light":"#999999"}},"("),s("span",{style:{"--shiki-dark":"#DBD7CAEE","--shiki-light":"#393A34"}},"m"),s("span",{style:{"--shiki-dark":"#666666","--shiki-light":"#999999"}},")")]),i(`
`),s("span",{class:"line"},[s("span",{style:{"--shiki-dark":"#4D9375","--shiki-light":"#1E754F"}},"        case"),s("span",{style:{"--shiki-dark":"#C99076","--shiki-light":"#A65E2B"}}," REPORT"),s("span",{style:{"--shiki-dark":"#666666","--shiki-light":"#999999"}},":"),s("span",{style:{"--shiki-dark":"#C99076","--shiki-light":"#A65E2B"}},"  self"),s("span",{style:{"--shiki-dark":"#666666","--shiki-light":"#999999"}},"."),s("span",{style:{"--shiki-dark":"#DBD7CAEE","--shiki-light":"#393A34"}},"reportACK"),s("span",{style:{"--shiki-dark":"#666666","--shiki-light":"#999999"}},"("),s("span",{style:{"--shiki-dark":"#DBD7CAEE","--shiki-light":"#393A34"}},"m"),s("span",{style:{"--shiki-dark":"#666666","--shiki-light":"#999999"}},")")]),i(`
`),s("span",{class:"line"},[s("span",{style:{"--shiki-dark":"#4D9375","--shiki-light":"#1E754F"}},"        case"),s("span",{style:{"--shiki-dark":"#DBD7CAEE","--shiki-light":"#393A34"}}," _"),s("span",{style:{"--shiki-dark":"#666666","--shiki-light":"#999999"}},":"),s("span",{style:{"--shiki-dark":"#4D9375","--shiki-light":"#1E754F"}},"       raise"),s("span",{style:{"--shiki-dark":"#B8A965","--shiki-light":"#998418"}}," RuntimeError"),s("span",{style:{"--shiki-dark":"#666666","--shiki-light":"#999999"}},"()")])])],-1),u=s("p",null,[s("img",{alt:"WorkerSM",width:"200px",class:"absolute top-35% left-60% right-0 bottom-0",src:_})],-1),K={__name:"8",setup(F){return E(k),A(),(v,P)=>{const l=p,e=n;return o(),d(m,c(y(h(D)(h(k),7))),{left:a(r=>[t(l,g({},{ranges:[]}),{default:a(()=>[B]),_:1},16)]),right:a(r=>[u,t(e,{variant:"white"})]),default:a(()=>[f,C]),_:1},16)}}};export{K as default};
