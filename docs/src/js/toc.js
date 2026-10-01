(function () {
    var defaults = {
        headings: 'h1, h2, h3, h4',
        scope: '.markdown-section',
        title: 'On this page',
        headerOffset: 80,
    };

    function plugin(hook, vm) {
        var options = Object.assign({}, defaults, vm.config.toc);
        var compact = window.matchMedia('(max-width: 1300px)');
        var nav;
        var details;
        var entries = [];
        var frame = null;

        function titleText() {
            return vm.config.toc.title || options.title;
        }

        function setActive(entry) {
            entries.forEach(function (item) {
                var active = item === entry;
                item.link.parentElement.classList.toggle('active', active);
                if (active) {
                    item.link.setAttribute('aria-current', 'location');
                } else {
                    item.link.removeAttribute('aria-current');
                }
            });
        }

        function updateActive() {
            frame = null;
            if (!entries.length) {
                return;
            }

            var active = entries[0];
            entries.forEach(function (entry) {
                if (entry.heading.getBoundingClientRect().top <= options.headerOffset) {
                    active = entry;
                }
            });
            setActive(active);
        }

        function scheduleActive() {
            if (frame === null) {
                frame = window.requestAnimationFrame(updateActive);
            }
        }

        function applyLayout() {
            if (details) {
                details.open = !compact.matches;
            }
            scheduleActive();
        }

        function buildTOC(scope) {
            var list = document.createElement('ul');
            var stack = [];

            scope.querySelectorAll(options.headings).forEach(function (heading) {
                if (!heading.id) {
                    return;
                }

                var level = Number(heading.tagName.slice(1));
                while (stack.length && stack[stack.length - 1].level >= level) {
                    stack.pop();
                }

                var parentList = list;
                if (stack.length) {
                    var parent = stack[stack.length - 1];
                    if (!parent.children) {
                        parent.children = document.createElement('ul');
                        parent.item.appendChild(parent.children);
                    }
                    parentList = parent.children;
                }

                var item = document.createElement('li');
                var link = document.createElement('a');
                var anchor = heading.querySelector('a.anchor[href]');
                link.textContent = heading.textContent.trim();
                link.href = anchor ? anchor.href : vm.router.toURL(vm.route.path, { id: heading.id });
                link.className = 'anchor';
                item.appendChild(link);
                parentList.appendChild(item);
                stack.push({ level: level, item: item });

                var entry = { heading: heading, link: link };
                entries.push(entry);
                link.addEventListener('click', function (event) {
                    if (event.button === 0 && !event.ctrlKey && !event.metaKey && !event.shiftKey && !event.altKey) {
                        setActive(entry);
                        if (compact.matches && details) {
                            details.open = false;
                        }
                    }
                    // Keep the native href so Docsify updates the chapter URL.
                });
            });

            return list;
        }

        hook.mounted(function () {
            var content = document.querySelector('.content');
            if (!content) {
                return;
            }

            nav = document.createElement('aside');
            nav.className = 'nav';
            nav.setAttribute('aria-label', titleText());
            nav.hidden = true;
            content.insertBefore(nav, content.firstChild);

            window.addEventListener('scroll', scheduleActive, { passive: true });
            window.addEventListener('resize', scheduleActive, { passive: true });
            window.addEventListener('hashchange', scheduleActive);
            compact.addEventListener('change', applyLayout);
        });

        hook.doneEach(function () {
            if (!nav) {
                return;
            }

            nav.textContent = '';
            nav.setAttribute('aria-label', titleText());
            nav.hidden = true;
            details = null;
            entries = [];

            var scope = document.querySelector(options.scope);
            if (!scope) {
                return;
            }

            var list = buildTOC(scope);
            if (!entries.length) {
                return;
            }

            details = document.createElement('details');
            details.className = 'page_toc';
            details.open = !compact.matches;

            var title = document.createElement('summary');
            title.className = 'title';
            title.textContent = titleText();
            details.appendChild(title);
            details.appendChild(list);
            details.addEventListener('toggle', scheduleActive);
            nav.appendChild(details);
            nav.hidden = false;
            scheduleActive();
        });
    }

    window.$docsify = window.$docsify || {};
    window.$docsify.plugins = [plugin].concat(window.$docsify.plugins || []);
})();
