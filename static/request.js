// request.js


export async function request(url, options = {}) {


  // 从 localStorage 获取 token
  const token = localStorage.getItem("token");

  // 如果 token 不存在，直接返回错误
  options.headers = options.headers || {};
  if (token) {
    options.headers["Authorization"] = "Bearer " + token;
  }
  try {
    const res = await fetch(url, options);
    const data = await res.json();
    if (!res.ok) {
      if (res.status === 401 || res.status === 403) {
        alert("登录状态失效，请重新登录");
        localStorage.clear();
        location.href = "login.html";
        return;
      }
      throw new Error(data.detail || "请求失败");
    }
    return data;
  } catch (error) {
    alert("请求错误：" + error.message);
    throw error;
  }
}
