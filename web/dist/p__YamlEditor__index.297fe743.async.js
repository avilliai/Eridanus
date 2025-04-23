"use strict";(self.webpackChunkant_design_pro=self.webpackChunkant_design_pro||[]).push([[445],{5578:function(De,L,n){n.r(L);var K=n(52677),x=n.n(K),S=n(19632),p=n.n(S),F=n(97857),Y=n.n(F),N=n(15009),m=n.n(N),z=n(99289),h=n.n(z),$=n(5574),P=n.n($),E=n(67294),V=n(34407),d=n(2453),w=n(72269),g=n(55102),G=n(37804),v=n(83622),j=n(223),b=n(4393),H=n(74330),C=n(34041),J=n(30291),Q=n(8298),X=n(82061),k=n(51042),q=n(15525),ee=n(74453),a=n(85893),Le=V.Z.Title,ne=function(){var ae=(0,E.useState)([]),O=P()(ae,2),re=O[0],se=O[1],_e=(0,E.useState)(""),M=P()(_e,2),y=M[0],I=M[1],te=(0,E.useState)({}),U=P()(te,2),f=U[0],W=U[1],ie=E.useState(!1),A=P()(ie,2),le=A[0],T=A[1],ue=function(){var l=h()(m()().mark(function r(){var i,_;return m()().wrap(function(e){for(;;)switch(e.prev=e.next){case 0:return e.prev=0,e.next=3,fetch("/api/files");case 3:if(i=e.sent,i.ok){e.next=6;break}throw new Error("\u7F51\u7EDC\u54CD\u5E94\u5931\u8D25");case 6:return e.next=8,i.json();case 8:_=e.sent,_.files?(se(_.files),_.files.length>0&&(I(_.files[0]),R(_.files[0]))):d.ZP.error("\u914D\u7F6E\u6587\u4EF6\u5217\u8868\u52A0\u8F7D\u5931\u8D25"),e.next=15;break;case 12:e.prev=12,e.t0=e.catch(0),d.ZP.error("\u83B7\u53D6\u6587\u4EF6\u5217\u8868\u65F6\u51FA\u9519: "+e.t0);case 15:case"end":return e.stop()}},r,null,[[0,12]])}));return function(){return l.apply(this,arguments)}}(),R=function(){var l=h()(m()().mark(function r(i){var _,t;return m()().wrap(function(s){for(;;)switch(s.prev=s.next){case 0:return s.prev=0,T(!0),s.next=4,fetch("/api/load/".concat(i));case 4:return _=s.sent,s.next=7,_.json();case 7:t=s.sent,t?(W(t),t.error&&d.ZP.error("\u9519\u8BEF\uFF1A".concat(t.error))):d.ZP.error("\u914D\u7F6E\u6587\u4EF6\u52A0\u8F7D\u5931\u8D25"),s.next=14;break;case 11:s.prev=11,s.t0=s.catch(0),d.ZP.error("\u914D\u7F6E\u6587\u4EF6\u52A0\u8F7D\u51FA\u9519: "+s.t0);case 14:return s.prev=14,T(!1),s.finish(14);case 17:case"end":return s.stop()}},r,null,[[0,11,14,17]])}));return function(i){return l.apply(this,arguments)}}(),de=function(){var l=h()(m()().mark(function r(){var i,_;return m()().wrap(function(e){for(;;)switch(e.prev=e.next){case 0:return e.prev=0,e.next=3,fetch("/api/save/".concat(y),{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(f)});case 3:return i=e.sent,e.next=6,i.json();case 6:_=e.sent,_.message?d.ZP.success("\u914D\u7F6E\u6587\u4EF6\u4FDD\u5B58\u6210\u529F"):d.ZP.error(_.error||"\u4FDD\u5B58\u5931\u8D25"),e.next=13;break;case 10:e.prev=10,e.t0=e.catch(0),d.ZP.error("\u4FDD\u5B58\u914D\u7F6E\u6587\u4EF6\u65F6\u51FA\u9519: "+e.t0);case 13:case"end":return e.stop()}},r,null,[[0,10]])}));return function(){return l.apply(this,arguments)}}(),c=function(r,i){for(var _=r.split("."),t=Y()({},f),e=t.data||t,s=0;s<_.length-1;s++){var u=_[s];if(u.includes("[")){var o=u.split("["),Z=P()(o,2),Pe=Z[0],ce=Z[1],Ee=parseInt(ce.replace("]",""),10);e=e[Pe][Ee]}else e=e[u]}var D=_[_.length-1];if(D.includes("[")){var fe=D.split("["),B=P()(fe,2),Ze=B[0],he=B[1],ve=parseInt(he.replace("]",""),10);e[Ze][ve]=i}else e[D]=i;W(t)},oe=function(r,i){return typeof r=="boolean"?(0,a.jsx)(w.Z,{checked:r,checkedChildren:"\u5F00",unCheckedChildren:"\u5173",onChange:function(t){return c(i,t)}}):typeof r=="string"?(0,a.jsx)(g.Z,{type:"text",value:r,onChange:function(t){return c(i,t.target.value)}}):typeof r=="number"?(0,a.jsx)(G.Z,{value:r,style:{width:"100%"},onChange:function(t){return c(i,t)}}):Array.isArray(r)?(0,a.jsxs)("div",{className:"array-container",children:[r.map(function(_,t){return(0,a.jsxs)("div",{className:"array-item",children:[(0,a.jsx)(g.Z,{value:_,onChange:function(s){var u=p()(r);u[t]=s.target.value,c(i,u)}}),(0,a.jsx)(v.ZP,{danger:!0,icon:(0,a.jsx)(X.Z,{}),onClick:function(){var s=r.filter(function(u,o){return o!==t});c(i,s)}})]},t)}),(0,a.jsx)(v.ZP,{type:"dashed",icon:(0,a.jsx)(k.Z,{}),onClick:function(){c(i,[].concat(p()(r),[""]))},children:"\u6DFB\u52A0\u9879"})]}):null},me=function l(r){var i=arguments.length>1&&arguments[1]!==void 0?arguments[1]:{},_=arguments.length>2&&arguments[2]!==void 0?arguments[2]:"",t=Object.keys(r);return(0,a.jsx)(j.Z,{dataSource:t,bordered:!1,split:!1,renderItem:function(s){var u=r[s],o=_?"".concat(_,".").concat(s):s,Z=i[o];return(0,a.jsx)(j.Z.Item,{className:"yaml-item",children:(0,a.jsxs)(b.Z,{style:{margin:"-8px"},className:"yaml-content",children:[(0,a.jsxs)("div",{className:"key-container",children:[(0,a.jsxs)("strong",{style:{fontSize:"1.2rem"},children:[s,":"]}),Z&&(0,a.jsx)("span",{style:{left:"5px"},className:"comment",dangerouslySetInnerHTML:{__html:Z.replace(/((?:https?:\/\/)?(?:(?:[a-z0-9]?(?:[a-z0-9\-]{1,61}[a-z0-9])?\.[^\.|\s])+[a-z\.]*[a-z]+|(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(?:\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)){3})(?::\d{1,5})*[a-z0-9.,_\/~#&=;%+?\-\\(\\)]*)/gi,'<a href="$&" target="_blank">$&</a>')}})]}),x()(u)==="object"&&!Array.isArray(u)?(0,a.jsx)("div",{className:"nested-object",children:l(u,i,o)}):oe(u,o)]})})}})};return(0,E.useEffect)(function(){ue()},[]),(0,a.jsx)(H.Z,{spinning:le,size:"large",children:(0,a.jsx)(ee._z,{children:(0,a.jsx)(b.Z,{children:(0,a.jsxs)("div",{className:"yaml-editor",children:[(0,a.jsx)("div",{className:"editor-header",children:(0,a.jsxs)("div",{className:"file-controls",children:[(0,a.jsx)(C.Z,{value:y,onChange:function(r){I(r),R(r)},style:{width:200},children:re.map(function(l){return(0,a.jsx)(C.Z.Option,{value:l,children:l},l)})}),(0,a.jsx)(J.Z,{offsetTop:60,children:(0,a.jsx)(v.ZP,{type:"primary",onClick:de,children:"\u4FDD\u5B58\u914D\u7F6E"})})]})}),(0,a.jsx)("div",{className:"editor-content",children:f.data&&me(f.data,f.comments)}),(0,a.jsx)(Q.Z,{icon:(0,a.jsx)(q.Z,{}),tooltip:"\u8FD4\u56DE\u9876\u90E8",type:"primary"}),(0,a.jsx)("style",{jsx:!0,children:`
        .yaml-editor {
          // padding: 20px;
        }
        .editor-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 20px;
        }
        .file-controls {
          display: flex;
          gap: 5px;
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
      `})]})})})})};L.default=ne}}]);
