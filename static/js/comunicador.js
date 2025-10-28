const fraseEl = document.getElementById('frase');


function adicionarPalavra(p){
const atual = fraseEl.textContent.trim();
fraseEl.textContent = (atual ? atual + ' ' : '') + p;
}
function limparFrase(){ fraseEl.textContent = ''; }
function falarFrase(){
const texto = fraseEl.textContent.trim();
if(!texto) return;
if('speechSynthesis' in window){
const u = new SpeechSynthesisUtterance(texto);
speechSynthesis.speak(u);
} else {
alert(texto);
}
}