import { Router } from 'itty-router';
import { calendarDayInfo } from './calendar'
import { bazi_custom } from './bazi'
import { dt2Jd } from './jd'

// Create a new router
const router = Router();

/*
Our index route, a simple hello world.
*/
router.get('/', (request) => {
	return new Response('Hello, world!');
});


router.get('/dayinfo', ({query}) => {
	if (!query) {
		return jsonResponse(false, 'Invalid parames!')
	}
	const year = query.y
	const month = query.m
	const day = query.d
	const hour = query.h
	if ((!year && year != 0) || (!month && month != 0) || (!day && day != 0) ) {
		return jsonResponse(false, 'Invalid parames!')
	}

	const data = calendarDayInfo(year, month, day, 3)
	return jsonResponse(true, 'success', data)
})

router.get('/bazi', ({query}) => {
	if (!query) {
		return jsonResponse(false, 'Invalid parames!')
	}
	const year = query.y
	const month = query.m
	const day = query.d
	const hour = query.h
	if ((!year && year != 0) || (!month && month != 0) || (!day && day != 0) ) {
		return jsonResponse(false, 'Invalid parames!')
	}

    //let jd = dt2Jd(year, month, day, hour, 0, 0)
    //console.log(jd)
    //const data = {data: jd}
	const data = bazi_custom(year, month, day, 12, 0,0, 0, 0.0)
	return jsonResponse(true, 'success', data)
})

function jsonResponse(isSuccess, msg, data) {
	const returnData = JSON.stringify({"success": isSuccess == true ? 1 : 0, "msg": msg, data: data}, null, 2);
	return new Response(returnData, {
		headers: {
            /*
            add_header 'Access-Control-Allow-Origin' $http_origin;   # 全局变量获得当前请求origin，带cookie的请求不支持*
			add_header 'Access-Control-Allow-Credentials' 'true';    # 为 true 可带上 cookie
			add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS';  # 允许请求方法
			add_header 'Access-Control-Allow-Headers' $http_access_control_request_headers;  # 允许请求的 header，可以为 *
			add_header 'Access-Control-Expose-Headers' 'Content-Length,Content-Range';
            */
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "*",
			'Content-Type': 'application/json',
		},
	});
}
/*
This route demonstrates path parameters, allowing you to extract fragments from the request
URL.

Try visit /example/hello and see the response.
*/
router.get('/example/:text', ({ params }) => {
	// Decode text like "Hello%20world" into "Hello world"
	let input = decodeURIComponent(params.text);
	console.log(params)
	// Serialise the input into a base64 string
	let base64 = btoa(input);

	// Return the HTML with the string to the client
	return new Response(`<p>Base64 encoding: <code>${base64}</code></p><code></code></p>`, {
		headers: {
			'Content-Type': 'text/html',
		},
	});
});

router.get('/download/:text', async ({ params }) => {
	try {
	let input = decodeURIComponent(params.text);
	// Serialise the input into a base64 string
	console.log(input)
	
	const url = 'https://raw.githubusercontent.com/coodajingang/ChineseCalendar/v2/scriptable/' + input;
	// const request = new Request(url, {method: 'GET'});
	// let res = await router.send(request)
  
	// console.log(res)
	// 获取响应正文
	const res = await fetch(url, {
		headers: {
			"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
			"Accept-Encoding": "gzip, deflate, br",
		  "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"
		},
	  });
	  const body = await res.text();
	// Return the HTML with the string to the client
	return new Response(body);
} catch (error) {
    console.error(error);
    return new Response('请求失败', { status: 500 });
  }
});

/*
This shows a different HTTP method, a POST.

Try send a POST request using curl or another tool.

Try the below curl command to send JSON:

$ curl -X POST <worker> -H "Content-Type: application/json" -d '{"abc": "def"}'
*/
router.post('/post', async request => {
	// Create a base object with some fields.
	let fields = {
		asn: request.cf.asn,
		colo: request.cf.colo,
	};

	// If the POST data is JSON then attach it to our response.
	if (request.headers.get('Content-Type') === 'application/json') {
		let json = await request.json();
		Object.assign(fields, { json });
	}

	// Serialise the JSON to a string.
	const returnData = JSON.stringify(fields, null, 2);

	return new Response(returnData, {
		headers: {
			'Content-Type': 'application/json',
		},
	});
});

/*
This is the last route we define, it will match anything that hasn't hit a route we've defined
above, therefore it's useful as a 404 (and avoids us hitting worker exceptions, so make sure to include it!).

Visit any page that doesn't exist (e.g. /foobar) to see it in action.
*/
router.all('*', () => new Response('404, not found!', { status: 404 }));

export default {
	fetch: router.handle,
};
