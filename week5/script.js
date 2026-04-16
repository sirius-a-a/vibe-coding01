// 功能：为网页添加交互功能

// 等待 HTML 加载完成后再执行（避免找不到元素）
document.addEventListener('DOMContentLoaded', function () {

    // ---------- 1. 获取页面元素 ----------
    // 获取表单
    const form = document.getElementById('demoForm');
    // 获取名字输入框
    const nameInput = document.getElementById('name');
    // 获取留言输入框
    const messageInput = document.getElementById('message');

    // ---------- 2. 创建一个用于显示留言的区域（动态添加） ----------
    // 找到内容卡片
    const contentCard = document.querySelector('.content-card');

    // 创建留言区域容器
    const messageSection = document.createElement('div');
    messageSection.className = 'message-section';
    messageSection.innerHTML = `
        <h3>📝 留言记录</h3>
        <ul id="messageList" class="message-list">
            <li class="empty-message">暂无留言，快来抢沙发吧！</li>
        </ul>
        <button id="clearBtn" class="clear-btn">🗑️ 清空所有留言</button>
    `;

    // 将留言区域添加到表单后面
    contentCard.appendChild(messageSection);

    // 获取留言列表元素
    const messageList = document.getElementById('messageList');
    // 获取清空按钮
    const clearBtn = document.getElementById('clearBtn');

    // 从 localStorage 加载保存的留言
    let messages = loadMessages();

    // 显示已保存的留言
    displayMessages();

    // ---------- 3. 表单提交事件（核心交互） ----------
    // 绑定表单的提交事件
    form.addEventListener('submit', function (event) {
        // 阻止表单默认提交行为（防止页面刷新）
        event.preventDefault();

        // 获取用户输入的值，并去除首尾空格
        const name = nameInput.value.trim();
        const message = messageInput.value.trim();

        // 验证：两个字段都不能为空
        if (name === '' || message === '') {
            // 显示错误提示
            showTemporaryMessage('请填写姓名和留言！', 'error');
            return;
        }

        // 创建新的留言对象
        const newMessage = {
            id: Date.now(),  // 用时间戳作为唯一ID
            name: name,
            message: message,
            time: new Date().toLocaleString()  // 记录留言时间
        };

        // 添加到留言数组
        messages.push(newMessage);

        // 保存到 localStorage
        saveMessages();

        // 更新页面显示
        displayMessages();

        // 清空输入框
        nameInput.value = '';
        messageInput.value = '';

        // 显示成功提示
        showTemporaryMessage('✅ 留言发布成功！', 'success');

        // 【验收点2】更改样式：让提交按钮暂时变色（可见的样式更改）
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalBg = submitBtn.style.background;
        submitBtn.style.background = 'linear-gradient(135deg, #4CAF50 0%, #45a049 100%)';
        setTimeout(() => {
            submitBtn.style.background = originalBg;
        }, 300);
    });

    // ---------- 4. 清空所有留言（第二个交互事件） ----------
    if (clearBtn) {
        clearBtn.addEventListener('click', function () {
            if (messages.length > 0 && confirm('确定要清空所有留言吗？')) {
                messages = [];
                saveMessages();
                displayMessages();
                showTemporaryMessage('🗑️ 所有留言已清空', 'info');

                // 【验收点2补充】更改样式：清空按钮变色
                const originalBg = clearBtn.style.background;
                clearBtn.style.background = '#ff4444';
                setTimeout(() => {
                    clearBtn.style.background = originalBg;
                }, 300);
            }
        });
    }

    // ---------- 辅助函数：保存留言到 localStorage ----------
    function saveMessages() {
        localStorage.setItem('guestbook_messages', JSON.stringify(messages));
    }

    // ---------- 辅助函数：从 localStorage 加载留言 ----------
    function loadMessages() {
        const saved = localStorage.getItem('guestbook_messages');
        if (saved) {
            try {
                return JSON.parse(saved);
            } catch (e) {
                return [];
            }
        }
        return [];
    }

    // ---------- 辅助函数：显示留言列表 ----------
    function displayMessages() {
        // 清空留言列表（保留 ul 元素本身）
        messageList.innerHTML = '';

        if (messages.length === 0) {
            // 没有留言时显示提示
            const emptyItem = document.createElement('li');
            emptyItem.className = 'empty-message';
            emptyItem.textContent = '暂无留言，快来抢沙发吧！';
            messageList.appendChild(emptyItem);
        } else {
            // 有留言时，遍历显示每条留言
            messages.forEach(msg => {
                const li = document.createElement('li');
                li.className = 'message-item';
                li.setAttribute('data-id', msg.id);
                li.innerHTML = `
                    <div class="message-header">
                        <strong class="message-name">👤 ${escapeHtml(msg.name)}</strong>
                        <span class="message-time">📅 ${escapeHtml(msg.time)}</span>
                    </div>
                    <div class="message-content">💬 ${escapeHtml(msg.message)}</div>
                    <button class="delete-message" data-id="${msg.id}">删除</button>
                `;
                messageList.appendChild(li);
            });

            // 为每个删除按钮绑定事件（事件委托也可以，这里直接绑定）
            document.querySelectorAll('.delete-message').forEach(btn => {
                btn.addEventListener('click', function (e) {
                    e.stopPropagation();
                    const id = parseInt(this.getAttribute('data-id'));
                    deleteMessageById(id);
                });
            });
        }
    }

    // ---------- 辅助函数：删除单条留言 ----------
    function deleteMessageById(id) {
        messages = messages.filter(msg => msg.id !== id);
        saveMessages();
        displayMessages();
        showTemporaryMessage('🗑️ 留言已删除', 'info');

        // 【验收点2补充】更改样式：临时改变背景
        const contentCard = document.querySelector('.content-card');
        const originalBg = contentCard.style.backgroundColor;
        contentCard.style.backgroundColor = '#fff9c4';
        setTimeout(() => {
            contentCard.style.backgroundColor = originalBg;
        }, 300);
    }

    // ---------- 辅助函数：显示临时提示消息 ----------
    function showTemporaryMessage(text, type = 'info') {
        // 创建提示元素
        const toast = document.createElement('div');
        toast.className = `toast-message toast-${type}`;
        toast.textContent = text;
        toast.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            padding: 12px 20px;
            background: ${type === 'error' ? '#ff4444' : (type === 'success' ? '#4CAF50' : '#2196F3')};
            color: white;
            border-radius: 8px;
            font-size: 14px;
            z-index: 1000;
            animation: slideIn 0.3s ease;
            box-shadow: 0 2px 10px rgba(0,0,0,0.2);
        `;

        document.body.appendChild(toast);

        // 3秒后自动消失
        setTimeout(() => {
            toast.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => {
                if (document.body.contains(toast)) {
                    document.body.removeChild(toast);
                }
            }, 300);
        }, 3000);
    }

    // ---------- 辅助函数：防止 XSS 攻击 ----------
    function escapeHtml(str) {
        if (!str) return '';
        return str
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }

    // ---------- 【验收点1】绑定点击事件 ----------
    // 方式1：直接通过 onclick 属性绑定（验收要求）
    // 在 HTML 中也可以，这里用 JS 方式再演示一个额外的点击事件

    // 给页面标题添加点击效果（额外的点击事件）
    const pageTitle = document.querySelector('header h1');
    if (pageTitle) {
        pageTitle.style.cursor = 'pointer';
        pageTitle.onclick = function () {
            // 点击标题时改变标题样式（可见更改）
            this.style.transform = 'scale(1.05)';
            this.style.transition = 'transform 0.3s';
            showTemporaryMessage('🎉 你点击了标题！', 'info');
            setTimeout(() => {
                this.style.transform = 'scale(1)';
            }, 500);
        };
    }

    // 给 Flex 示例添加点击效果（验收点）
    const flexDemo = document.querySelector('.flex-demo');
    if (flexDemo) {
        flexDemo.style.cursor = 'pointer';
        flexDemo.onclick = function () {
            // 【验收点2】点击后样式发生可见改变
            this.style.backgroundColor = 'rgba(255, 255, 255, 0.5)';
            this.style.transform = 'scale(1.02)';
            this.innerHTML = '🎉 你点了我！这是用 JavaScript 改变的内容 🎉';
            setTimeout(() => {
                this.style.backgroundColor = 'rgba(255, 255, 255, 0.2)';
                this.style.transform = 'scale(1)';
                setTimeout(() => {
                    this.innerHTML = '🎯 这是用 Flex 实现的内容居中示例（再点一下试试）';
                }, 2000);
            }, 1000);
        };
    }

    // 添加动画样式
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        @keyframes slideOut {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(100%);
                opacity: 0;
            }
        }
        .message-section {
            margin-top: 30px;
            padding-top: 20px;
            border-top: 2px dashed #e0e0e0;
        }
        .message-section h3 {
            color: #764ba2;
            margin-bottom: 15px;
        }
        .message-list {
            list-style: none;
            margin-bottom: 15px;
            max-height: 300px;
            overflow-y: auto;
        }
        .message-item {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 12px;
            margin-bottom: 10px;
            border-left: 4px solid #667eea;
            transition: all 0.2s;
        }
        .message-item:hover {
            transform: translateX(5px);
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .message-header {
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
            flex-wrap: wrap;
        }
        .message-name {
            color: #667eea;
        }
        .message-time {
            font-size: 12px;
            color: #999;
        }
        .message-content {
            color: #333;
            line-height: 1.4;
        }
        .delete-message {
            background: #ff4444;
            color: white;
            border: none;
            padding: 4px 12px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 12px;
            margin-top: 8px;
            transition: all 0.2s;
        }
        .delete-message:hover {
            background: #cc0000;
            transform: scale(1.02);
        }
        .empty-message {
            color: #999;
            text-align: center;
            padding: 20px;
            font-style: italic;
        }
        .clear-btn {
            background: #ff9800;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s;
            width: auto;
            display: inline-block;
        }
        .clear-btn:hover {
            background: #f57c00;
            transform: translateY(-2px);
        }
    `;
    document.head.appendChild(style);
});