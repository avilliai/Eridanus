"use strict";(self.webpackChunkant_design_pro=self.webpackChunkant_design_pro||[]).push([[445],{5578:function(Le,D,a){a.r(D);var K=a(52677),F=a.n(K),S=a(19632),b=a.n(S),Y=a(97857),w=a.n(Y),N=a(15009),m=a.n(N),z=a(99289),Z=a.n(z),V=a(5574),c=a.n(V),p=a(67294),H=a(55102),d=a(2453),$=a(72269),G=a(37804),J=a(86738),v=a(83622),j=a(223),C=a(4393),Q=a(34041),X=a(74330),k=a(64218),q=a(82061),ee=a(51042),ne=a(34804),n=a(85893),L="",O=H.Z.TextArea,ae=function(){var re=(0,p.useState)([]),M=c()(re,2),se=M[0],te=M[1],_e=(0,p.useState)(""),y=c()(_e,2),I=y[0],A=y[1],ie=(0,p.useState)({}),U=c()(ie,2),P=U[0],W=U[1],le=(0,p.useState)(!1),T=c()(le,2),ue=T[0],R=T[1],de=function(){var u=Z()(m()().mark(function r(){var _,s;return m()().wrap(function(e){for(;;)switch(e.prev=e.next){case 0:return e.prev=0,e.next=3,fetch("".concat(L,"/api/files"));case 3:if(_=e.sent,_.ok){e.next=6;break}throw new Error("\u7F51\u7EDC\u54CD\u5E94\u5931\u8D25");case 6:return e.next=8,_.json();case 8:s=e.sent,s.files?(te(s.files),s.files.length>0&&(A(s.files[0]),x(s.files[0]))):d.ZP.error("\u914D\u7F6E\u6587\u4EF6\u5217\u8868\u52A0\u8F7D\u5931\u8D25"),e.next=15;break;case 12:e.prev=12,e.t0=e.catch(0),d.ZP.error("\u83B7\u53D6\u6587\u4EF6\u5217\u8868\u65F6\u51FA\u9519: "+e.t0);case 15:case"end":return e.stop()}},r,null,[[0,12]])}));return function(){return u.apply(this,arguments)}}(),x=function(){var u=Z()(m()().mark(function r(_){var s,t;return m()().wrap(function(i){for(;;)switch(i.prev=i.next){case 0:return i.prev=0,R(!0),i.next=4,fetch("".concat(L,"/api/load/").concat(_));case 4:return s=i.sent,i.next=7,s.json();case 7:t=i.sent,t?(W(t),t.error&&d.ZP.error("\u9519\u8BEF\uFF1A".concat(t.error))):d.ZP.error("\u914D\u7F6E\u6587\u4EF6\u52A0\u8F7D\u5931\u8D25"),i.next=14;break;case 11:i.prev=11,i.t0=i.catch(0),d.ZP.error("\u914D\u7F6E\u6587\u4EF6\u52A0\u8F7D\u51FA\u9519: "+i.t0);case 14:return i.prev=14,R(!1),i.finish(14);case 17:case"end":return i.stop()}},r,null,[[0,11,14,17]])}));return function(_){return u.apply(this,arguments)}}(),oe=function(){var u=Z()(m()().mark(function r(){var _,s;return m()().wrap(function(e){for(;;)switch(e.prev=e.next){case 0:return e.prev=0,e.next=3,fetch("".concat(L,"/api/save/").concat(I),{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(P)});case 3:return _=e.sent,e.next=6,_.json();case 6:s=e.sent,s.message?d.ZP.success("\u914D\u7F6E\u6587\u4EF6\u4FDD\u5B58\u6210\u529F"):d.ZP.error(s.error||"\u4FDD\u5B58\u5931\u8D25"),e.next=13;break;case 10:e.prev=10,e.t0=e.catch(0),d.ZP.error("\u4FDD\u5B58\u914D\u7F6E\u6587\u4EF6\u65F6\u51FA\u9519: "+e.t0);case 13:case"end":return e.stop()}},r,null,[[0,10]])}));return function(){return u.apply(this,arguments)}}(),E=function(r,_){for(var s=r.split("."),t=w()({},P),e=t.data||t,i=0;i<s.length-1;i++){var l=s[i];if(l.includes("[")){var o=l.split("["),f=c()(o,2),h=f[0],Ee=f[1],fe=parseInt(Ee.replace("]",""),10);e=e[h][fe]}else e=e[l]}var g=s[s.length-1];if(g.includes("[")){var pe=g.split("["),B=c()(pe,2),he=B[0],Ze=B[1],ve=parseInt(Ze.replace("]",""),10);e[he][ve]=_}else e[g]=_;W(t)},me=function(r,_){return typeof r=="boolean"?(0,n.jsx)($.Z,{checked:r,checkedChildren:"\u5F00",unCheckedChildren:"\u5173",onChange:function(t){return E(_,t)}}):typeof r=="string"?(0,n.jsx)(O,{value:r,onChange:function(t){return E(_,t.target.value)},autoSize:{minRows:1,maxRows:5}}):typeof r=="number"?(0,n.jsx)(G.Z,{type:"number",value:r,style:{width:"100%"},onChange:function(t){t==null||E(_,t)}}):Array.isArray(r)?(0,n.jsxs)("div",{className:"array-container",children:[r.map(function(s,t){return(0,n.jsxs)("div",{className:"array-item",children:[(0,n.jsx)(O,{value:s,onChange:function(i){var l=b()(r);l[t]=i.target.value,E(_,l)},autoSize:{minRows:1,maxRows:5}}),(0,n.jsx)(J.Z,{title:"\u786E\u8BA4\u5220\u9664\u5417\uFF1F",placement:"topRight",onConfirm:function(){var i=r.filter(function(l,o){return o!==t});E(_,i)},okText:"\u662F",cancelText:"\u5426",children:(0,n.jsx)(v.ZP,{danger:!0,icon:(0,n.jsx)(q.Z,{})})})]},t)}),(0,n.jsx)(v.ZP,{type:"dashed",icon:(0,n.jsx)(ee.Z,{}),onClick:function(){E(_,[].concat(b()(r),[""]))},children:"\u6DFB\u52A0\u9879"})]}):null},ce=function u(r){var _=arguments.length>1&&arguments[1]!==void 0?arguments[1]:{},s=arguments.length>2&&arguments[2]!==void 0?arguments[2]:{},t=arguments.length>3&&arguments[3]!==void 0?arguments[3]:"",e=s[t]||Object.keys(r);return(0,n.jsx)(j.Z,{dataSource:e,bordered:!1,split:!1,renderItem:function(l){var o=r[l],f=t?"".concat(t,".").concat(l):l,h=_[f];return(0,n.jsx)(j.Z.Item,{className:"yaml-item",children:(0,n.jsxs)(C.Z,{style:{padding:0},className:"yaml-content",children:[(0,n.jsxs)("div",{className:"key-container",children:[(0,n.jsxs)("strong",{style:{fontSize:"1.2rem"},children:[l,":"]}),h&&(0,n.jsx)("span",{style:{left:"10px",opacity:.8,overflow:"hidden",textOverflow:"ellipsis",whiteSpace:"nowrap",display:"block",maxWidth:"100%"},className:"comment",dangerouslySetInnerHTML:{__html:h.replace(/((?:https?:\/\/)?(?:(?:[a-z0-9]?(?:[a-z0-9\-]{1,61}[a-z0-9])?\.[^\.|\s])+[a-z\.]*[a-z]+|(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(?:\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)){3})(?::\d{1,5})*[a-z0-9.,_\/~#&=;%+?\-\\(\\)]*)/gi,'<a href="$&" target="_blank">$&</a>')}})]}),F()(o)==="object"&&!Array.isArray(o)?(0,n.jsx)("div",{className:"nested-object",children:u(o,_,s,f)}):me(o,f)]})})}})};(0,p.useEffect)(function(){de()},[]);var Pe=function(){return(0,n.jsxs)(n.Fragment,{children:[(0,n.jsx)(Q.Z,{style:{width:"100%"},value:I||void 0,placeholder:"\u9009\u62E9\u6587\u4EF6",onChange:function(_){A(_),x(_)},suffixIcon:(0,n.jsx)(ne.Z,{}),options:se.map(function(r){return{value:r,label:r}})}),(0,n.jsx)(v.ZP,{type:"primary",onClick:oe,style:{marginLeft:"8px"},children:"\u4FDD\u5B58\u914D\u7F6E"})]})};return(0,n.jsx)(X.Z,{spinning:ue,size:"large",children:(0,n.jsx)(C.Z,{style:{padding:0},children:(0,n.jsxs)("div",{className:"yaml-editor",children:[(0,n.jsx)(k.Z,{offsetTop:60,children:(0,n.jsx)("div",{className:"file-controls",children:(0,n.jsx)(Pe,{})})}),(0,n.jsx)("div",{className:"editor-content",children:P.data&&ce(P.data,P.comments,P.order)}),(0,n.jsx)("style",{children:`
        .yaml-editor {
          // padding: 20px;
        }
        .file-controls {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 20px;
          display: flex;
          gap: 5px;
          padding: 5px;
        }
        .yaml-item {
          // border: 1px solid #e8e8e8;
          // padding: 5px;
          // margin-bottom: 10px;
          border-radius: 5px;
        }
        .yaml-content {
          width: 100%;
        }
        .key-container {
          margin-bottom: 8px;
        }
        .comment {
          margin-left: 8px;
        }
        .nested-object {
          margin-left: 20px;
        }
        .array-container {
          display: flex;
          flex-direction: column;
          gap: 8px;
        }
        .array-item {
          display: flex;
          gap: 8px;
          align-items: center;
        }
      `})]})})})};D.default=ae}}]);
