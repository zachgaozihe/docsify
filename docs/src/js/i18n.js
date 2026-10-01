(function () {
    var prefix = '/zh-cn';
    var descriptions = {
        en: "Zach Gao's computer science and AI learning library: learning paths, open courses, university notes and technical articles.",
        'zh-cn': 'Zach Gao 的计算机科学与人工智能学习知识库：学习路线、公开课程、大学课程笔记和技术文章。',
    };

    function language(path) {
        return /^\/zh-cn(?:\/|$)/.test(path) ? 'zh-cn' : 'en';
    }

    function translatedPath(path, target) {
        var page = path.replace(/^\/zh-cn(?=\/|$)/, '') || '/';
        return target === 'zh-cn' ? prefix + (page === '/' ? '/' : page) : page;
    }

    function plugin(hook, vm) {
        function updateLinks() {
            var current = language(vm.route.path);
            document.querySelectorAll('a[data-site-language]').forEach(function (link) {
                var target = link.dataset.siteLanguage;
                link.href = '#' + translatedPath(vm.route.path, target);
                link.classList.toggle('language-active', target === current);
                if (target === current) link.setAttribute('aria-current', 'true');
                else link.removeAttribute('aria-current');
                link.title = target === 'zh-cn' ? '切换到当前页面的中文版' : 'Read this page in English';
            });
        }

        function updateLanguage() {
            var current = language(vm.route.path);
            document.documentElement.lang = current === 'zh-cn' ? 'zh-CN' : 'en';
            document.querySelector('meta[name="description"]').content = descriptions[current];
            document.querySelector('meta[property="og:description"]').content = descriptions[current];
            vm.config.toc.title = current === 'zh-cn' ? '本页目录' : 'On this page';
            return current;
        }

        hook.beforeEach(function (text) {
            updateLanguage();
            return text;
        });

        hook.mounted(function () {
            // Docsify can finish loading a navbar after doneEach has run.
            // Keep ordinary links and new-tab destinations on the same article.
            var navbar = document.querySelector('.app-nav');
            if (navbar) new MutationObserver(updateLinks).observe(navbar, { childList: true, subtree: true });
            updateLinks();
            document.addEventListener('click', function (event) {
                var link = event.target.closest('a[data-site-language]');
                if (!link || event.button !== 0 || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
                event.preventDefault();
                // Each translated article has its own chapter IDs: switch the
                // article and return to its start rather than reuse a stale ID.
                var destination = translatedPath(vm.route.path, link.dataset.siteLanguage);
                if (destination === vm.route.path) return;
                window.location.hash = destination;
            });
        });

        hook.doneEach(function () {
            updateLanguage();
            updateLinks();
        });
    }

    window.$docsify.plugins = [plugin].concat(window.$docsify.plugins || []);
})();
