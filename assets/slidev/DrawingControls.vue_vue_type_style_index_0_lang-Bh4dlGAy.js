import{l as X,m as G,n as I,o as J,p as O,q as Q,r as W,s as Z,t as nn,u as en,v as tn,w as sn}from"../modules/unplugin-icons-vksyP9w5.js";import{d as L,t as h,H as on,X as ln,o as g,b as V,f as an,h as z,A as n,c as x,k as o,l as t,i as l,e as i,x as rn,R as m,S as un,F as cn,V as dn,Y as b,g as pn}from"../modules/vue-DaYSqhD_.js";import{L as _n}from"../modules/shiki-DLxQYbt2.js";import{u as mn}from"./DrawingPreview.vue_vue_type_script_setup_true_lang-76vui8hi.js";import{V as D}from"./useWakeLock-CeXYHvSj.js";import{_ as a}from"./IconButton.vue_vue_type_script_setup_true_lang-BHrx_Ps5.js";const gn=L({__name:"Draggable",props:{storageKey:{},initial:{}},setup($){const u=$,w=h(null),f=u.initial??{x:0,y:0},k=u.storageKey?on(u.storageKey,f):h(f),{style:y}=ln(w,{initialValue:k});return(v,d)=>(g(),V("div",{ref_key:"el",ref:w,class:"fixed",style:z(n(y))},[an(v.$slots,"default")],4))}}),wn={class:"flex bg-main p-2"},fn={class:"inline-block w-7 text-center"},vn={class:"pt-.5"},hn=L({__name:"DrawingControls",setup($){const{brush:u,canClear:w,canRedo:f,canUndo:k,clear:y,drauu:v,drawingEnabled:d,drawingMode:r,drawingPinned:c,brushColors:B}=mn();function M(){v.undo()}function S(){v.redo()}let C="stylus";function p(_){r.value=_,d.value=!0,_!=="eraseLine"&&(C=_)}function R(_){u.color=_,d.value=!0,r.value=C}return(_,e)=>{const U=X,A=G,E=I,K=J,N=O,F=Q,P=W,Y=Z,j=nn,q=en,H=tn,T=sn;return g(),x(gn,{class:l(["flex flex-wrap text-xl p-2 gap-1 rounded-md bg-main shadow transition-opacity duration-200 z-20 border border-main",n(d)?"":n(c)?"opacity-40 hover:opacity-90":"opacity-0 pointer-events-none"]),"storage-key":"slidev-drawing-pos","initial-x":10,"initial-y":10},{default:o(()=>[t(a,{title:"Draw with stylus",class:l({shallow:n(r)!=="stylus"}),onClick:e[0]||(e[0]=s=>p("stylus"))},{default:o(()=>[t(U)]),_:1},8,["class"]),t(a,{title:"Draw a line",class:l({shallow:n(r)!=="line"}),onClick:e[1]||(e[1]=s=>p("line"))},{default:o(()=>e[13]||(e[13]=[i("svg",{width:"1em",height:"1em",class:"-mt-0.5",preserveAspectRatio:"xMidYMid meet",viewBox:"0 0 24 24"},[i("path",{d:"M21.71 3.29a1 1 0 0 0-1.42 0l-18 18a1 1 0 0 0 0 1.42a1 1 0 0 0 1.42 0l18-18a1 1 0 0 0 0-1.42z",fill:"currentColor"})],-1)])),_:1},8,["class"]),t(a,{title:"Draw an arrow",class:l({shallow:n(r)!=="arrow"}),onClick:e[2]||(e[2]=s=>p("arrow"))},{default:o(()=>[t(A)]),_:1},8,["class"]),t(a,{title:"Draw an ellipse",class:l({shallow:n(r)!=="ellipse"}),onClick:e[3]||(e[3]=s=>p("ellipse"))},{default:o(()=>[t(E)]),_:1},8,["class"]),t(a,{title:"Draw a rectangle",class:l({shallow:n(r)!=="rectangle"}),onClick:e[4]||(e[4]=s=>p("rectangle"))},{default:o(()=>[t(K)]),_:1},8,["class"]),t(a,{title:"Erase",class:l({shallow:n(r)!=="eraseLine"}),onClick:e[5]||(e[5]=s=>p("eraseLine"))},{default:o(()=>[t(N)]),_:1},8,["class"]),t(D),t(n(_n),null,{popper:o(()=>[i("div",wn,[i("div",fn,rn(n(u).size),1),i("div",vn,[m(i("input",{"onUpdate:modelValue":e[6]||(e[6]=s=>n(u).size=s),type:"range",min:"1",max:"15",onChange:e[7]||(e[7]=s=>r.value=n(C))},null,544),[[un,n(u).size]])])])]),default:o(()=>[t(a,{title:"Adjust stroke width",class:l({shallow:n(r)==="eraseLine"})},{default:o(()=>e[14]||(e[14]=[i("svg",{viewBox:"0 0 32 32",width:"1.2em",height:"1.2em"},[i("line",{x1:"2",y1:"15",x2:"22",y2:"4",stroke:"currentColor","stroke-width":"1","stroke-linecap":"round"}),i("line",{x1:"2",y1:"24",x2:"28",y2:"10",stroke:"currentColor","stroke-width":"2","stroke-linecap":"round"}),i("line",{x1:"7",y1:"31",x2:"29",y2:"19",stroke:"currentColor","stroke-width":"3","stroke-linecap":"round"})],-1)])),_:1},8,["class"])]),_:1}),(g(!0),V(cn,null,dn(n(B),s=>(g(),x(a,{key:s,title:"Set brush color",class:l(n(u).color===s&&n(r)!=="eraseLine"?"active":"shallow"),onClick:bn=>R(s)},{default:o(()=>[i("div",{class:l(["w-6 h-6 transition-all transform border",n(u).color!==s?"rounded-1/2 scale-85 border-white":"rounded-md border-gray-300/50"]),style:z(n(d)?{background:s}:{borderColor:s})},null,6)]),_:2},1032,["class","onClick"]))),128)),t(D),t(a,{title:"Undo",class:l({disabled:!n(k)}),onClick:e[8]||(e[8]=s=>M())},{default:o(()=>[t(F)]),_:1},8,["class"]),t(a,{title:"Redo",class:l({disabled:!n(f)}),onClick:e[9]||(e[9]=s=>S())},{default:o(()=>[t(P)]),_:1},8,["class"]),t(a,{title:"Delete",class:l({disabled:!n(w)}),onClick:e[10]||(e[10]=s=>n(y)())},{default:o(()=>[t(Y)]),_:1},8,["class"]),t(D),t(a,{title:n(c)?"Unpin drawing":"Pin drawing",class:l({shallow:!n(c)}),onClick:e[11]||(e[11]=s=>c.value=!n(c))},{default:o(()=>[m(t(j,{class:"transform -rotate-45"},null,512),[[b,n(c)]]),m(t(q,null,null,512),[[b,!n(c)]])]),_:1},8,["title","class"]),n(d)?(g(),x(a,{key:0,title:n(c)?"Drawing pinned":"Drawing unpinned",class:l({shallow:!n(d)}),onClick:e[12]||(e[12]=s=>d.value=!n(d))},{default:o(()=>[m(t(H,null,null,512),[[b,n(c)]]),m(t(T,null,null,512),[[b,!n(c)]])]),_:1},8,["title","class"])):pn("v-if",!0)]),_:1},8,["class"])}}});export{hn as _};
