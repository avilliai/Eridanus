"use strict";(self.webpackChunkant_design_pro=self.webpackChunkant_design_pro||[]).push([[445],{5578:function(ge,D,r){r.r(D);var B=r(52677),K=r.n(B),S=r(19632),L=r.n(S),F=r(97857),Y=r.n(F),z=r(15009),m=r.n(z),N=r(99289),h=r.n(N),w=r(5574),P=r.n(w),E=r(67294),V=r(55102),u=r(2453),H=r(72269),$=r(37804),G=r(86738),Z=r(83622),g=r(223),j=r(4393),J=r(85418),C=r(50136),Q=r(42075),X=r(74330),k=r(64218),q=r(82061),ee=r(51042),ne=r(34804),re=r(74453),n=r(85893),b=V.Z.TextArea,ae=function(){var se=(0,E.useState)([]),O=P()(se,2),te=O[0],_e=O[1],ie=(0,E.useState)(""),M=P()(ie,2),y=M[0],I=M[1],le=(0,E.useState)({}),A=P()(le,2),f=A[0],W=A[1],de=(0,E.useState)(!1),T=P()(de,2),ue=T[0],U=T[1],oe=function(){var d=h()(m()().mark(function a(){var _,s;return m()().wrap(function(e){for(;;)switch(e.prev=e.next){case 0:return e.prev=0,e.next=3,fetch("/api/files");case 3:if(_=e.sent,_.ok){e.next=6;break}throw new Error("\u7F51\u7EDC\u54CD\u5E94\u5931\u8D25");case 6:return e.next=8,_.json();case 8:s=e.sent,s.files?(_e(s.files),s.files.length>0&&(I(s.files[0]),R(s.files[0]))):u.ZP.error("\u914D\u7F6E\u6587\u4EF6\u5217\u8868\u52A0\u8F7D\u5931\u8D25"),e.next=15;break;case 12:e.prev=12,e.t0=e.catch(0),u.ZP.error("\u83B7\u53D6\u6587\u4EF6\u5217\u8868\u65F6\u51FA\u9519: "+e.t0);case 15:case"end":return e.stop()}},a,null,[[0,12]])}));return function(){return d.apply(this,arguments)}}(),R=function(){var d=h()(m()().mark(function a(_){var s,i;return m()().wrap(function(t){for(;;)switch(t.prev=t.next){case 0:return t.prev=0,U(!0),t.next=4,fetch("/api/load/".concat(_));case 4:return s=t.sent,t.next=7,s.json();case 7:i=t.sent,i?(W(i),i.error&&u.ZP.error("\u9519\u8BEF\uFF1A".concat(i.error))):u.ZP.error("\u914D\u7F6E\u6587\u4EF6\u52A0\u8F7D\u5931\u8D25"),t.next=14;break;case 11:t.prev=11,t.t0=t.catch(0),u.ZP.error("\u914D\u7F6E\u6587\u4EF6\u52A0\u8F7D\u51FA\u9519: "+t.t0);case 14:return t.prev=14,U(!1),t.finish(14);case 17:case"end":return t.stop()}},a,null,[[0,11,14,17]])}));return function(_){return d.apply(this,arguments)}}(),me=function(){var d=h()(m()().mark(function a(){var _,s;return m()().wrap(function(e){for(;;)switch(e.prev=e.next){case 0:return e.prev=0,e.next=3,fetch("/api/save/".concat(y),{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(f)});case 3:return _=e.sent,e.next=6,_.json();case 6:s=e.sent,s.message?u.ZP.success("\u914D\u7F6E\u6587\u4EF6\u4FDD\u5B58\u6210\u529F"):u.ZP.error(s.error||"\u4FDD\u5B58\u5931\u8D25"),e.next=13;break;case 10:e.prev=10,e.t0=e.catch(0),u.ZP.error("\u4FDD\u5B58\u914D\u7F6E\u6587\u4EF6\u65F6\u51FA\u9519: "+e.t0);case 13:case"end":return e.stop()}},a,null,[[0,10]])}));return function(){return d.apply(this,arguments)}}(),c=function(a,_){for(var s=a.split("."),i=Y()({},f),e=i.data||i,t=0;t<s.length-1;t++){var l=s[t];if(l.includes("[")){var o=l.split("["),v=P()(o,2),fe=v[0],ve=v[1],Ze=parseInt(ve.replace("]",""),10);e=e[fe][Ze]}else e=e[l]}var p=s[s.length-1];if(p.includes("[")){var he=p.split("["),x=P()(he,2),pe=x[0],De=x[1],Le=parseInt(De.replace("]",""),10);e[pe][Le]=_}else e[p]=_;W(i)},Pe=function(a,_){return typeof a=="boolean"?(0,n.jsx)(H.Z,{checked:a,checkedChildren:"\u5F00",unCheckedChildren:"\u5173",onChange:function(i){return c(_,i)}}):typeof a=="string"?(0,n.jsx)(b,{value:a,onChange:function(i){return c(_,i.target.value)},autoSize:{minRows:1,maxRows:5}}):typeof a=="number"?(0,n.jsx)($.Z,{type:"number",value:a,style:{width:"100%"},onChange:function(i){c(_,i)}}):Array.isArray(a)?(0,n.jsxs)("div",{className:"array-container",children:[a.map(function(s,i){return(0,n.jsxs)("div",{className:"array-item",children:[(0,n.jsx)(b,{value:s,onChange:function(t){var l=L()(a);l[i]=t.target.value,c(_,l)},autoSize:{minRows:1,maxRows:5}}),(0,n.jsx)(G.Z,{title:"\u786E\u8BA4\u5220\u9664\u5417\uFF1F",placement:"topRight",onConfirm:function(){var t=a.filter(function(l,o){return o!==i});c(_,t)},okText:"\u662F",cancelText:"\u5426",children:(0,n.jsx)(Z.ZP,{danger:!0,icon:(0,n.jsx)(q.Z,{})})})]},i)}),(0,n.jsx)(Z.ZP,{type:"dashed",icon:(0,n.jsx)(ee.Z,{}),onClick:function(){c(_,[].concat(L()(a),[""]))},children:"\u6DFB\u52A0\u9879"})]}):null},ce=function d(a){var _=arguments.length>1&&arguments[1]!==void 0?arguments[1]:{},s=arguments.length>2&&arguments[2]!==void 0?arguments[2]:"",i=Object.keys(a);return(0,n.jsx)(g.Z,{dataSource:i,bordered:!1,split:!1,renderItem:function(t){var l=a[t],o=s?"".concat(s,".").concat(t):t,v=_[o];return(0,n.jsx)(g.Z.Item,{className:"yaml-item",children:(0,n.jsxs)(j.Z,{style:{padding:0},className:"yaml-content",children:[(0,n.jsxs)("div",{className:"key-container",children:[(0,n.jsxs)("strong",{style:{fontSize:"1.2rem"},children:[t,":"]}),v&&(0,n.jsx)("span",{style:{left:"10px",opacity:.8,overflow:"hidden",textOverflow:"ellipsis",whiteSpace:"nowrap",display:"block",maxWidth:"100%"},className:"comment",dangerouslySetInnerHTML:{__html:v.replace(/((?:https?:\/\/)?(?:(?:[a-z0-9]?(?:[a-z0-9\-]{1,61}[a-z0-9])?\.[^\.|\s])+[a-z\.]*[a-z]+|(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(?:\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)){3})(?::\d{1,5})*[a-z0-9.,_\/~#&=;%+?\-\\(\\)]*)/gi,'<a href="$&" target="_blank">$&</a>')}})]}),K()(l)==="object"&&!Array.isArray(l)?(0,n.jsx)("div",{className:"nested-object",children:d(l,_,o)}):Pe(l,o)]})})}})};(0,E.useEffect)(function(){oe()},[]);var Ee=function(){return(0,n.jsxs)(n.Fragment,{children:[(0,n.jsx)(J.Z,{autoAdjustOverflow:!0,overlay:(0,n.jsx)(C.Z,{onClick:function(_){var s=_.key;I(s),R(s)},children:te.map(function(a){return(0,n.jsx)(C.Z.Item,{children:a},a)})}),children:(0,n.jsx)(Z.ZP,{style:{width:"100%"},onClick:function(_){return _.preventDefault()},children:(0,n.jsxs)(Q.Z,{children:[y||"\u9009\u62E9\u6587\u4EF6",(0,n.jsx)(ne.Z,{style:{marginRight:"0"}})]})})}),(0,n.jsx)(Z.ZP,{type:"primary",onClick:me,style:{marginLeft:"8px"},children:"\u4FDD\u5B58\u914D\u7F6E"})]})};return(0,n.jsx)(X.Z,{spinning:ue,size:"large",children:(0,n.jsx)(re._z,{children:(0,n.jsx)(j.Z,{style:{padding:0},children:(0,n.jsxs)("div",{className:"yaml-editor",children:[(0,n.jsx)(k.Z,{offsetTop:60,children:(0,n.jsx)("div",{className:"file-controls",children:(0,n.jsx)(Ee,{})})}),(0,n.jsx)("div",{className:"editor-content",children:f.data&&ce(f.data,f.comments)}),(0,n.jsx)("style",{children:`
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
      `})]})})})})};D.default=ae}}]);
