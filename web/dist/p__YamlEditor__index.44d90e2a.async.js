"use strict";(self.webpackChunkant_design_pro=self.webpackChunkant_design_pro||[]).push([[445],{5578:function(ve,g,a){a.r(g);var B=a(52677),K=a.n(B),F=a(19632),D=a.n(F),S=a(97857),Y=a.n(S),w=a(15009),m=a.n(w),N=a(99289),Z=a.n(N),z=a(5574),P=a.n(z),p=a(67294),V=a(55102),d=a(2453),H=a(72269),$=a(37804),G=a(86738),v=a(83622),b=a(223),j=a(4393),J=a(34041),Q=a(74330),X=a(64218),k=a(82061),q=a(51042),ee=a(34804),n=a(85893),C=V.Z.TextArea,ne=function(){var ae=(0,p.useState)([]),O=P()(ae,2),re=O[0],se=O[1],te=(0,p.useState)(""),M=P()(te,2),y=M[0],I=M[1],_e=(0,p.useState)({}),A=P()(_e,2),c=A[0],W=A[1],ie=(0,p.useState)(!1),T=P()(ie,2),le=T[0],U=T[1],ue=function(){var u=Z()(m()().mark(function r(){var t,s;return m()().wrap(function(e){for(;;)switch(e.prev=e.next){case 0:return e.prev=0,e.next=3,fetch("/api/files");case 3:if(t=e.sent,t.ok){e.next=6;break}throw new Error("\u7F51\u7EDC\u54CD\u5E94\u5931\u8D25");case 6:return e.next=8,t.json();case 8:s=e.sent,s.files?(se(s.files),s.files.length>0&&(I(s.files[0]),R(s.files[0]))):d.ZP.error("\u914D\u7F6E\u6587\u4EF6\u5217\u8868\u52A0\u8F7D\u5931\u8D25"),e.next=15;break;case 12:e.prev=12,e.t0=e.catch(0),d.ZP.error("\u83B7\u53D6\u6587\u4EF6\u5217\u8868\u65F6\u51FA\u9519: "+e.t0);case 15:case"end":return e.stop()}},r,null,[[0,12]])}));return function(){return u.apply(this,arguments)}}(),R=function(){var u=Z()(m()().mark(function r(t){var s,_;return m()().wrap(function(i){for(;;)switch(i.prev=i.next){case 0:return i.prev=0,U(!0),i.next=4,fetch("/api/load/".concat(t));case 4:return s=i.sent,i.next=7,s.json();case 7:_=i.sent,_?(W(_),_.error&&d.ZP.error("\u9519\u8BEF\uFF1A".concat(_.error))):d.ZP.error("\u914D\u7F6E\u6587\u4EF6\u52A0\u8F7D\u5931\u8D25"),i.next=14;break;case 11:i.prev=11,i.t0=i.catch(0),d.ZP.error("\u914D\u7F6E\u6587\u4EF6\u52A0\u8F7D\u51FA\u9519: "+i.t0);case 14:return i.prev=14,U(!1),i.finish(14);case 17:case"end":return i.stop()}},r,null,[[0,11,14,17]])}));return function(t){return u.apply(this,arguments)}}(),de=function(){var u=Z()(m()().mark(function r(){var t,s;return m()().wrap(function(e){for(;;)switch(e.prev=e.next){case 0:return e.prev=0,e.next=3,fetch("/api/save/".concat(y),{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(c)});case 3:return t=e.sent,e.next=6,t.json();case 6:s=e.sent,s.message?d.ZP.success("\u914D\u7F6E\u6587\u4EF6\u4FDD\u5B58\u6210\u529F"):d.ZP.error(s.error||"\u4FDD\u5B58\u5931\u8D25"),e.next=13;break;case 10:e.prev=10,e.t0=e.catch(0),d.ZP.error("\u4FDD\u5B58\u914D\u7F6E\u6587\u4EF6\u65F6\u51FA\u9519: "+e.t0);case 13:case"end":return e.stop()}},r,null,[[0,10]])}));return function(){return u.apply(this,arguments)}}(),E=function(r,t){for(var s=r.split("."),_=Y()({},c),e=_.data||_,i=0;i<s.length-1;i++){var l=s[i];if(l.includes("[")){var o=l.split("["),f=P()(o,2),h=f[0],ce=f[1],Ee=parseInt(ce.replace("]",""),10);e=e[h][Ee]}else e=e[l]}var L=s[s.length-1];if(L.includes("[")){var fe=L.split("["),x=P()(fe,2),pe=x[0],he=x[1],Ze=parseInt(he.replace("]",""),10);e[pe][Ze]=t}else e[L]=t;W(_)},oe=function(r,t){return typeof r=="boolean"?(0,n.jsx)(H.Z,{checked:r,checkedChildren:"\u5F00",unCheckedChildren:"\u5173",onChange:function(_){return E(t,_)}}):typeof r=="string"?(0,n.jsx)(C,{value:r,onChange:function(_){return E(t,_.target.value)},autoSize:{minRows:1,maxRows:5}}):typeof r=="number"?(0,n.jsx)($.Z,{type:"number",value:r,style:{width:"100%"},onChange:function(_){E(t,_)}}):Array.isArray(r)?(0,n.jsxs)("div",{className:"array-container",children:[r.map(function(s,_){return(0,n.jsxs)("div",{className:"array-item",children:[(0,n.jsx)(C,{value:s,onChange:function(i){var l=D()(r);l[_]=i.target.value,E(t,l)},autoSize:{minRows:1,maxRows:5}}),(0,n.jsx)(G.Z,{title:"\u786E\u8BA4\u5220\u9664\u5417\uFF1F",placement:"topRight",onConfirm:function(){var i=r.filter(function(l,o){return o!==_});E(t,i)},okText:"\u662F",cancelText:"\u5426",children:(0,n.jsx)(v.ZP,{danger:!0,icon:(0,n.jsx)(k.Z,{})})})]},_)}),(0,n.jsx)(v.ZP,{type:"dashed",icon:(0,n.jsx)(q.Z,{}),onClick:function(){E(t,[].concat(D()(r),[""]))},children:"\u6DFB\u52A0\u9879"})]}):null},me=function u(r){var t=arguments.length>1&&arguments[1]!==void 0?arguments[1]:{},s=arguments.length>2&&arguments[2]!==void 0?arguments[2]:{},_=arguments.length>3&&arguments[3]!==void 0?arguments[3]:"",e=s[_]||Object.keys(r);return(0,n.jsx)(b.Z,{dataSource:e,bordered:!1,split:!1,renderItem:function(l){var o=r[l],f=_?"".concat(_,".").concat(l):l,h=t[f];return(0,n.jsx)(b.Z.Item,{className:"yaml-item",children:(0,n.jsxs)(j.Z,{style:{padding:0},className:"yaml-content",children:[(0,n.jsxs)("div",{className:"key-container",children:[(0,n.jsxs)("strong",{style:{fontSize:"1.2rem"},children:[l,":"]}),h&&(0,n.jsx)("span",{style:{left:"10px",opacity:.8,overflow:"hidden",textOverflow:"ellipsis",whiteSpace:"nowrap",display:"block",maxWidth:"100%"},className:"comment",dangerouslySetInnerHTML:{__html:h.replace(/((?:https?:\/\/)?(?:(?:[a-z0-9]?(?:[a-z0-9\-]{1,61}[a-z0-9])?\.[^\.|\s])+[a-z\.]*[a-z]+|(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(?:\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)){3})(?::\d{1,5})*[a-z0-9.,_\/~#&=;%+?\-\\(\\)]*)/gi,'<a href="$&" target="_blank">$&</a>')}})]}),K()(o)==="object"&&!Array.isArray(o)?(0,n.jsx)("div",{className:"nested-object",children:u(o,t,s,f)}):oe(o,f)]})})}})};(0,p.useEffect)(function(){ue()},[]);var Pe=function(){return(0,n.jsxs)(n.Fragment,{children:[(0,n.jsx)(J.Z,{style:{width:"100%"},value:y||void 0,placeholder:"\u9009\u62E9\u6587\u4EF6",onChange:function(t){I(t),R(t)},suffixIcon:(0,n.jsx)(ee.Z,{}),options:re.map(function(r){return{value:r,label:r}})}),(0,n.jsx)(v.ZP,{type:"primary",onClick:de,style:{marginLeft:"8px"},children:"\u4FDD\u5B58\u914D\u7F6E"})]})};return(0,n.jsx)(Q.Z,{spinning:le,size:"large",children:(0,n.jsx)(j.Z,{style:{padding:0},children:(0,n.jsxs)("div",{className:"yaml-editor",children:[(0,n.jsx)(X.Z,{offsetTop:60,children:(0,n.jsx)("div",{className:"file-controls",children:(0,n.jsx)(Pe,{})})}),(0,n.jsx)("div",{className:"editor-content",children:c.data&&me(c.data,c.comments,c.order)}),(0,n.jsx)("style",{children:`
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
      `})]})})})};g.default=ne}}]);
