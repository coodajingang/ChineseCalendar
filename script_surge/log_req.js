let headers = $request.headers;
let url = $request.url;
console.log(headers);
console.log(url);

$done({headers});