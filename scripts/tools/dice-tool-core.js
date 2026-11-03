/* Dice converter core: pure functions, no DOM, no network.
   WORDLIST is injected at build time from the kit Python file. */
var WORDLIST = /*__WORDLIST__*/[];

/* SHA-256: byte array in, 32 byte array out. */
function sha256(data){
  function rotr(x,n){ return (x>>>n)|(x<<(32-n)); }
  var K=[0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,
  0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,
  0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,
  0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,
  0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,
  0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,
  0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,
  0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2];
  var H=[0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19];
  var bytes=Array.prototype.slice.call(data);
  var bitLen=bytes.length*8;
  bytes.push(0x80);
  while(bytes.length%64!==56) bytes.push(0);
  var hi=Math.floor(bitLen/4294967296), lo=bitLen>>>0;
  bytes.push((hi>>>24)&255,(hi>>>16)&255,(hi>>>8)&255,hi&255,
             (lo>>>24)&255,(lo>>>16)&255,(lo>>>8)&255,lo&255);
  var w=new Array(64), i, b;
  for(b=0;b<bytes.length;b+=64){
    for(i=0;i<16;i++) w[i]=((bytes[b+i*4]<<24)|(bytes[b+i*4+1]<<16)|(bytes[b+i*4+2]<<8)|bytes[b+i*4+3])>>>0;
    for(i=16;i<64;i++){
      var s0=(rotr(w[i-15],7)^rotr(w[i-15],18)^(w[i-15]>>>3))>>>0;
      var s1=(rotr(w[i-2],17)^rotr(w[i-2],19)^(w[i-2]>>>10))>>>0;
      w[i]=(w[i-16]+s0+w[i-7]+s1)>>>0;
    }
    var a=H[0],bb=H[1],c=H[2],d=H[3],e=H[4],f=H[5],g=H[6],h=H[7];
    for(i=0;i<64;i++){
      var S1=(rotr(e,6)^rotr(e,11)^rotr(e,25))>>>0;
      var ch=((e&f)^(~e&g))>>>0;
      var t1=(h+S1+ch+K[i]+w[i])>>>0;
      var S0=(rotr(a,2)^rotr(a,13)^rotr(a,22))>>>0;
      var maj=((a&bb)^(a&c)^(bb&c))>>>0;
      var t2=(S0+maj)>>>0;
      h=g;g=f;f=e;e=(d+t1)>>>0;d=c;c=bb;bb=a;a=(t1+t2)>>>0;
    }
    H[0]=(H[0]+a)>>>0;H[1]=(H[1]+bb)>>>0;H[2]=(H[2]+c)>>>0;H[3]=(H[3]+d)>>>0;
    H[4]=(H[4]+e)>>>0;H[5]=(H[5]+f)>>>0;H[6]=(H[6]+g)>>>0;H[7]=(H[7]+h)>>>0;
  }
  var out=[];
  for(i=0;i<8;i++) out.push((H[i]>>>24)&255,(H[i]>>>16)&255,(H[i]>>>8)&255,H[i]&255);
  return out;
}

function bytesToBits(bytes){
  var s='';
  for(var i=0;i<bytes.length;i++) s+=bytes[i].toString(2).padStart(8,'0');
  return s;
}
/* Mirror the Python tool: pad left with zeros to a whole number of bytes. */
function bitsToBytes(bitstr){
  var s=bitstr;
  var r=s.length%8;
  if(r!==0) s='0'.repeat(8-r)+s;
  var out=[];
  for(var i=0;i<s.length;i+=8) out.push(parseInt(s.slice(i,i+8),2));
  return out;
}
function cleanBinary(s){
  s = s || '';
  // Remove ordinary whitespace, keep only 0s and 1s
  var stripped = s.replace(/[ \n\t\r]/g, '');
  if (!stripped) {
    throw new Error('No valid binary digits (0 or 1) found');
  }
  var invalid = stripped.replace(/[01]/g, '');
  if (invalid) {
    var chars = {};
    for (var i = 0; i < invalid.length; i++) chars[invalid[i]] = true;
    throw new Error('Invalid characters found: ' + Object.keys(chars).join(', '));
  }
  return stripped;
}
/* The guide's face map: 1=00 2=01 3=10 4=11. 5 and 6 are not bits. */
function faceToBits(face){
  return {1:'00',2:'01',3:'10',4:'11'}[face] || null;
}
/* 256 bits of entropy -> 24 words. Checksum is the first 8 bits of SHA-256(entropy). */
function bitsToWords(bits256){
  var entropyBytes=bitsToBytes(bits256);
  var checkBits=bytesToBits(sha256(entropyBytes)).slice(0,8);
  var full=bits256+checkBits;
  var words=[];
  for(var i=0;i<24;i++) words.push(WORDLIST[parseInt(full.slice(i*11,(i+1)*11),2)]);
  return words;
}
/* Accept 256 bits or more, like the Python tool. Longer input is hashed down. */
function wordsFromBitsInput(raw){
  var bits;
  try {
    bits = cleanBinary(raw);
  } catch (e) {
    return {words:null, note:e.message};
  }
  var note='';
  if(bits.length<256) return {words:null, note:'Need 256 bits. Pasted text holds '+bits.length+'.'};
  if(bits.length>256){
    bits=bytesToBits(sha256(bitsToBytes(bits)));
    note='Pasted '+bits.length+' bits. Hashed down to 256, like the Python tool.';
  }
  return {words:bitsToWords(bits), note:note, bits:bits};
}
/* Validate a 24 word list: word list membership plus the checksum. */
function validateWords(arr){
  var words=(arr||[]).map(function(w){return (w||'').toLowerCase();}).filter(function(w){return w.length>0;});
  if(words.length!==24) return {ok:false, reason:'Need 24 words. Found '+words.length+'.'};
  var bad=[];
  for(var i=0;i<24;i++) if(WORDLIST.indexOf(words[i])<0) bad.push(i+1);
  if(bad.length) return {ok:false, reason:'Not in the word list, positions: '+bad.join(', ')+'.'};
  var bits='';
  for(i=0;i<24;i++) bits+=WORDLIST.indexOf(words[i]).toString(2).padStart(11,'0');
  var expect=bytesToBits(sha256(bitsToBytes(bits.slice(0,256)))).slice(0,8);
  if(expect!==bits.slice(256)) return {ok:false, reason:'The check word does not match the other 23. One of the words is wrong.'};
  return {ok:true, reason:'All 24 words are in the list and the check word passes.'};
}
/* Word by word compare of two lists. The guide's "two tools must agree" step. */
function compareLists(aWords,bWords){
  var a=(aWords||[]).map(function(w){return (w||'').toLowerCase();}).filter(function(w){return w.length>0;});
  var b=(bWords||[]).map(function(w){return (w||'').toLowerCase();}).filter(function(w){return w.length>0;});
  if(a.length!==24||b.length!==24) return {ok:false, mismatches:[], reason:'Both lists need 24 words.'};
  var mismatches=[];
  for(var i=0;i<24;i++) if(a[i]!==b[i]) mismatches.push(i+1);
  return {ok:mismatches.length===0, mismatches:mismatches,
    reason:mismatches.length===0?'24 of 24 match.':'Differ at positions: '+mismatches.join(', ')+'.'};
}
if(typeof module!=='undefined') module.exports={sha256:sha256,bytesToBits:bytesToBits,bitsToBytes:bitsToBytes,cleanBinary:cleanBinary,faceToBits:faceToBits,bitsToWords:bitsToWords,wordsFromBitsInput:wordsFromBitsInput,validateWords:validateWords,compareLists:compareLists,WORDLIST:WORDLIST};
