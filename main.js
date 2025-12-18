// frontend main.js (same DSA demo: linked list + bubble sort + AJAX)
class Node { 
  constructor(contact){
     this.contact = contact;
      this.next = null;
     }
  }
class LinkedList {
  constructor(){
     this.head = null; 
    }
  append(contact){
     const node = new Node(contact);
      if(!this.head){ this.head = node; 
    return;   
      } let cur=this.head; while(cur.next) cur=cur.next; cur.next=node; }
  toArray(){
    const arr=[]; 
    let cur=this.head; 
    while(cur){
    arr.push(cur.contact);
    cur=cur.next }
    return arr;
  }
  findByNameOrPhone(q){
    q=q.toLowerCase();
    let cur=this.head; 
    const res=[]; 
    while(cur){
      const c=cur.contact; 
      if(c.name.toLowerCase().includes(q)||c.phone.toLowerCase().includes(q)) res.push(c);
      cur=cur.next 
    } 
    return res;
  }
}
function bubbleSortByName(arr){
  const a=arr.slice();
   for(let i=0;i<a.length;i++){
     for(let j=0;j<a.length-1-i;j++){
       if(a[j].name.toLowerCase() > a[j+1].name.toLowerCase()){
         [a[j],a[j+1]]=[a[j+1],a[j]] 
        }
       }
     } return a;
}
async function api(path, method='GET', body=null){
  const opts = { method, headers:{'Content-Type':'application/json'} };
  if(body) opts.body = JSON.stringify(body);
  const res = await fetch('/api'+path, opts);
  if(res.status>=400) throw await res.json();
  return res.json();
}
let contactsList = new LinkedList();
async function loadContacts(){
  const data = await api('/contacts');
  contactsList = new LinkedList();
  data.forEach(c=>contactsList.append(c));
  renderContacts(contactsList.toArray());
}
function renderContacts(arr){
  const container = document.getElementById('contactsList');
  if(!container) return;
  container.innerHTML='';
  if(arr.length===0){ container.innerHTML = '<p style="color:#6b7280">No contacts yet.</p>'; return; }
  arr.forEach(c=>{
    const d = document.createElement('div'); d.className='contact';
    d.innerHTML = `<h3>${escapeHtml(c.name)}</h3><p>${escapeHtml(c.phone)}</p><p class="meta">${escapeHtml(c.email||'')}</p>
      <div style="margin-top:8px;display:flex;gap:8px;">
        <button class="btn small" onclick="goEdit(${c.id})">Edit</button>
        <button class="btn small outline" onclick="doDelete(${c.id})">Delete</button>
      </div>`;
    container.appendChild(d);
  });
}
function escapeHtml(s){ if(!s) return ''; return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }
function goEdit(id){ window.location.href='/edit/'+id; }
async function doDelete(id){ if(!confirm('Delete this contact?')) return; await api('/contacts/'+id,'DELETE'); await loadContacts(); }

if(document.getElementById('addForm')){
  document.getElementById('addForm').addEventListener('submit', async (e)=>{
    e.preventDefault();
    const name=document.getElementById('name').value.trim();
    const phone=document.getElementById('phone').value.trim();
    const email=document.getElementById('email').value.trim();
    try{ await api('/contacts','POST',{name,phone,email}); document.getElementById('addForm').reset(); await loadContacts(); } catch(err){ alert(err.error || 'Failed'); }
  });
}
if(document.getElementById('searchInput')){
  document.getElementById('searchInput').addEventListener('input',(e)=>{
    const q=e.target.value.trim(); if(!q){ renderContacts(contactsList.toArray()); return; } renderContacts(contactsList.findByNameOrPhone(q));
  });
  document.getElementById('sortBtn').addEventListener('click', ()=> renderContacts(bubbleSortByName(contactsList.toArray())));
  document.getElementById('refreshBtn').addEventListener('click', ()=> loadContacts());
}
if(typeof contactId !== 'undefined'){
  window.addEventListener('DOMContentLoaded', async ()=>{
    try{
      const data = await api('/contacts/'+contactId);
      document.getElementById('ename').value = data.name;
      document.getElementById('ephone').value = data.phone;
      document.getElementById('eemail').value = data.email || '';
      document.getElementById('editForm').addEventListener('submit', async (e)=>{
        e.preventDefault();
        const name=document.getElementById('ename').value.trim();
        const phone=document.getElementById('ephone').value.trim();
        const email=document.getElementById('eemail').value.trim();
        await api('/contacts/'+contactId,'PUT',{name,phone,email});
        window.location.href='/';
      });
    }catch(err){ alert('Contact not found'); window.location.href='/'; }
  });
}
if(document.getElementById('contactsList')){ window.addEventListener('DOMContentLoaded', ()=> loadContacts()); }
