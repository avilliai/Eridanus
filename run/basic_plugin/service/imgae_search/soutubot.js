const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');

// 复用之前提供的 x-api-key 生成函数
function base64Encode(str) {
    try {
        if (typeof Buffer !== 'undefined') {
            return Buffer.from(str, 'utf8').toString('base64');
        }
    } catch (e) {
        console.error("Base64 encoding failed:", e);
        return '';
    }
}

function base64Decode(str) {
    try {
        if (typeof Buffer !== 'undefined') {
            return Buffer.from(str, 'base64').toString('utf8');
        }
    } catch (e) {
        console.error("Base64 decoding failed:", e);
        return '';
    }
}

function calculateSauceValue(userAgentString, mValue) {
    const unixTimestamp = Math.floor(Date.now() / 1000);
    const userAgentLength = userAgentString ? userAgentString.length : 0;
    const intermediateValue = (
        Math.pow(unixTimestamp, 2) +
        Math.pow(userAgentLength, 2) +
        (mValue || 0)
    ).toString();
    const encodedValue = base64Encode(intermediateValue);
    const reversedValue = encodedValue.split("").reverse().join("");
    const finalValue = reversedValue.replace(/=/g, "");
    return finalValue;
}

function calculateSauceKeyHeader(userAgentString, mValue) {
    const encodedKeyPart1 = "V0MxaFVHa3RTMFY1";
    const decodedKeyPart1 = base64Decode(encodedKeyPart1);
    const decodedKeyPart2 = base64Decode(decodedKeyPart1);
    const headerKey = decodedKeyPart2.toUpperCase();
    const headerValue = calculateSauceValue(userAgentString, mValue);
    return {
        headerKey: headerKey,
        headerValue: headerValue
    };
}

// 请求参数
const mValueFromGlobal = 12345;
const userAgentString = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 Edg/135.0.0.0';

// 生成 x-api-key
const result = calculateSauceKeyHeader(userAgentString, mValueFromGlobal);
const xApiKey = result.headerValue;

console.log("Generated x-api-key:", xApiKey);

// 构造 multipart/form-data 请求
const form = new FormData();
form.append('file', fs.createReadStream('D:\\BlueArchive\\Eridanus\\test.jpg')); // 替换为实际文件路径
form.append('factor', '1.2');

// 发送请求
async function sendRequest() {
    try {
        const response = await axios.post('https://soutubot.moe/api/search', form, {
            headers: {
                'x-api-key': xApiKey,
                'user-agent': userAgentString,
                'accept': 'application/json, text/plain, */*',
                'accept-encoding': 'gzip, deflate, br, zstd',
                'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
                'content-type': `multipart/form-data; boundary=${form.getBoundary()}`,
                'origin': 'https://soutubot.moe',
                'referer': 'https://soutubot.moe/',
                'sec-ch-ua': '"Microsoft Edge";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
                'x-requested-with': 'XMLHttpRequest',
                // 可选：添加 cookie
                'cookie': '_ga=GA1.1.1740252243.1738313083; _ga_JB369TC9SF=GS1.1.1745399308.4.0.1745399308.0.0.0; cf_clearance=gMvicuVNtBvbXFideeYLzecbmO6CtKxGZvnfvaXxnUc-1745399309-1.2.1.1-mdurm1WfYBTbuCc7Qx7qAzcLptiUdIU9yKol8zA1YbdTSP0.rPhte4Zk.a.L.LfLF_.QYUJRhMKUUag2J2B4lViQ1_RKwif_gWpmjPeG6NeGIOFmxniiy7szS4cFdc0xsmgLqGG2QuaFe5IjorSg.7iEMsWSvlmIesijhhnUSlLgtdlDjLkTYkrtvTfN7gILAuelx8F0R.cw3poQKcHvxZLlc28pZCk_o4SsnHTwIwoAz90k85mJAv0X1LfppaeJfI83P6NoySSnOetI_QN7823VEZoySfmMM4pQKEmCmRz5JFVG29zDjH.O4LGVuiydTFalo6GZpwYYzXy48SuCXtbc5MLDa46v9o.cgabqbPc'
            }
        });

        console.log('Response Status:', response.status);
        console.log('Response Data:', response.data);
    } catch (error) {
        console.error('Request Failed:', error.response ? error.response.data : error.message);
    }
}

sendRequest();