(function(){
 const mk=()=>{const f=function(){};return new Proxy(f,{
  get:(t,k)=>{ if(k==='domElement')return document.createElement('canvas'); if(k===Symbol.toPrimitive)return()=>0; if(k==='count')return 24;
    if(k==='then')return undefined; if(k==='length')return 0; return mk()},
  apply:()=>mk(), construct:()=>mk(), set:()=>true, has:()=>true})};
 window.THREE=new Proxy({},{get:(t,k)=>k==='then'?undefined:function(){return mk()}});
 window.__mock=true;
})();
