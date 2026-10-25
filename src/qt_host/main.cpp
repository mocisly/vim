#include "vim_runtime_api.h"

#include <QApplication>
#include <QCloseEvent>
#include <QCoreApplication>
#include <QDir>
#include <QHBoxLayout>
#include <QLabel>
#include <QTimer>
#include <QWidget>
#include <QWindow>

#include <array>
#include <cstdio>
#include <cstring>
#include <string>
#include <utility>
#include <windows.h>

namespace {

class VimHost final : public QWidget
{
public:
    explicit VimHost(bool selfTest, bool pythonTest, bool closeRetryTest,
                     std::string pythonQuitMode)
        : selfTest_(selfTest), pythonTest_(pythonTest), closeRetryTest_(closeRetryTest),
          pythonQuitMode_(std::move(pythonQuitMode)),
          selfTestDirectory_(QDir::fromNativeSeparators(
              QCoreApplication::applicationDirPath()).toLocal8Bit().constData())
    {
        if (selfTest_)
        {
            const std::string logPath = selfTestPath("vim-qt-host-selftest.log");
            (void)fopen_s(&selfTestLog_, logPath.c_str(), "w");
            DeleteFileA(selfTestPath("vim-qt-probe-A.leave").c_str());
            DeleteFileA(selfTestPath("vim-qt-probe-A.destroyed").c_str());
            DeleteFileA(selfTestPath("vim-qt-probe-B.after-a").c_str());
            DeleteFileA(selfTestPath("vim-qt-probe-A.finally").c_str());
            DeleteFileA(selfTestPath("vim-qt-gui-dialog-A.log").c_str());
            DeleteFileA(selfTestPath("vim-qt-gui-dialog-B.log").c_str());
            for (const char *name : {"A", "B"})
            {
                char scriptName[32];
                char resultName[32];
                std::snprintf(scriptName, sizeof(scriptName),
                              "vim-qt-probe-%s.vim", name);
                std::snprintf(resultName, sizeof(resultName),
                              "vim-qt-probe-%s.result", name);
                const std::string scriptPath = selfTestPath(scriptName);
                const std::string resultPath = selfTestPath(resultName);
                DeleteFileA(resultPath.c_str());
                std::FILE *script = nullptr;
                if (fopen_s(&script, scriptPath.c_str(), "w") != 0
                    || script == nullptr)
                    failed_ = true;
                else
                {
                    std::fprintf(script,
                                 "set nomore\n"
                                 "let g:qt_instance = '%s'\n"
                                 "call timer_start(100, {-> winnr('$') == 1 && "
                                 "&lines >= 4 ? execute('split') : ''}, "
                                 "{'repeat': 15})\n"
                                 "call timer_start(1700, {-> writefile([g:qt_instance, "
                                 "string(winnr('$')), string(&lines), "
                                 "string(&columns), v:errmsg], '%s')})\n",
                                 name, resultPath.c_str());
                    if (closeRetryTest_)
                    {
                        const auto cancelledPath = selfTestPath(
                            name[0] == 'A' ? "vim-qt-probe-A.cancelled"
                                           : "vim-qt-probe-B.cancelled");
                        DeleteFileA(cancelledPath.c_str());
                        std::fprintf(script,
                                     "autocmd QuitPre * ++once call writefile(['cancelled'], '%s') | close\n",
                                     cancelledPath.c_str());
                    }
                    if (pythonTest_)
                    {
                        const std::string pythonPath = selfTestPath(
                            name[0] == 'A' ? "vim-qt-probe-A.python"
                                           : "vim-qt-probe-B.python");
                        DeleteFileA(pythonPath.c_str());
                        std::fprintf(script,
                                     "if has('python3')\n"
                                     "  python3 import vim; plugin_owner = vim.eval('g:qt_instance')\n"
                                     "  python3 import sys; sys.path.insert(0, '%s'); import runtime_python_probe; runtime_python_probe.start()\n"
                                     "  py3do return line\n"
                                     "  set nomodified\n"
                                     "  call timer_start(600, {-> execute('python3 vim.command(\"let g:python_marker = \" + repr(plugin_owner))')})\n"
                                     "  call timer_start(800, {-> execute('python3 runtime_python_probe.callback()')})\n"
                                     "  call timer_start(1000, {-> get(g:, 'python_plugin_checked', '') == g:qt_instance ? writefile([get(g:, 'python_marker', 'missing')], '%s') : 0})\n"
                                     "else\n"
                                     "  call writefile(['unsupported'], '%s')\n"
                                     "endif\n",
                                     selfTestDirectory_.c_str(), pythonPath.c_str(), pythonPath.c_str());
                        if (name[0] == 'A')
                        {
                            std::fprintf(script,
                                         "python3 import sys, types; sys.modules['vim_dual_probe'] = types.SimpleNamespace(stale=vim.vars)\n"
                                         "autocmd VimLeavePre * call writefile(['A'], '%s')\n",
                                         selfTestPath("vim-qt-probe-A.leave").c_str());
                            if (!pythonQuitMode_.empty())
                                std::fprintf(script,
                                    "let g:python_quit_mode = '%s'\n"
                                    "let g:python_finally_path = '%s'\n"
                                    "call timer_start(2200, {-> execute('%s')})\n",
                                    pythonQuitMode_.c_str(),
                                    selfTestPath("vim-qt-probe-A.finally").c_str(),
                                    pythonQuitMode_ == "pydo"
                                        ? "py3do import runtime_python_probe; runtime_python_probe.quit_instance()"
                                        : "python3 runtime_python_probe.quit_instance()");
                        }
                        else
                            std::fprintf(script,
                                         "function! QtProbeAfterA(timer)\n"
                                         "  if filereadable('%s') && !exists('g:qt_after_a')\n"
                                         "    call garbagecollect(1)\n"
                                         "    python3 runtime_python_probe.after_a(); vim.command('let g:python_after_a_ok = 1')\n"
                                         "    python3 vim.command(\"let g:qt_after_a = \" + repr(plugin_owner))\n"
                                         "    if get(g:, 'python_after_a_ok', 0) | call writefile([g:qt_after_a], '%s') | endif\n"
                                         "  endif\n"
                                         "endfunction\n"
                                         "call timer_start(200, function('QtProbeAfterA'), {'repeat': 30})\n",
                                         selfTestPath("vim-qt-probe-A.destroyed").c_str(),
                                         selfTestPath("vim-qt-probe-B.after-a").c_str());
                    }
                    std::fclose(script);
                }
            }
        }
        logEvent("host starting");
        setWindowTitle(QStringLiteral("Vim Qt Host"));
        resize(1280, 720);
        setMinimumSize(800, 480);
        layout_ = new QHBoxLayout(this);
        layout_->setContentsMargins(0, 0, 0, 0);

        for (std::size_t index = 0; index < instances_.size(); ++index)
        {
            placeholders_[index] = new QLabel(
                index == 0 ? QStringLiteral("正在启动 Vim A…")
                           : QStringLiteral("正在启动 Vim B…"), this);
            placeholders_[index]->setAlignment(Qt::AlignCenter);
            placeholders_[index]->setAttribute(Qt::WA_NativeWindow);
            placeholders_[index]->setMinimumSize(320, 240);
            layout_->addWidget(placeholders_[index], 1);
            parentWindows_[index] = reinterpret_cast<HWND>(
                placeholders_[index]->winId());

            // Give Vim a real HWND before its GUI starts. Vim's --windowid
            // path parents the native window here before showing it, so it
            // never appears as a separate top-level window.
            char windowId[32]{};
            std::snprintf(windowId, sizeof(windowId), "0x%llx",
                          static_cast<unsigned long long>(
                    reinterpret_cast<quintptr>(parentWindows_[index])));
            const std::string dialogPath = selfTestPath(
                index == 0 ? "vim-qt-gui-dialog-A.log"
                           : "vim-qt-gui-dialog-B.log");
            const std::string scriptPath = selfTestPath(
                index == 0 ? "vim-qt-probe-A.vim"
                           : "vim-qt-probe-B.vim");
            const std::array<const char *, 16> testArguments = {
                "vim", "-g", "-f", "-N", "--windowid", windowId,
                "-u", "NONE", "-U", "NONE",
                "-i", "NONE", "--gui-dialog-file", dialogPath.c_str(),
                "-S", scriptPath.c_str()
            };
            const std::array<const char *, 6> normalArguments = {
                "vim", "-g", "-f", "-N", "--windowid", windowId
            };
            instances_[index] = selfTest_
                ? vim_runtime_instance_create(
                    static_cast<int>(testArguments.size()), testArguments.data())
                : vim_runtime_instance_create(
                    static_cast<int>(normalArguments.size()), normalArguments.data());
            if (instances_[index] == nullptr)
            {
                failed_ = true;
                std::fprintf(stderr, "Could not start Vim instance %zu\n", index + 1);
            }
            else
                logEvent(index == 0 ? "created A" : "created B");
        }

        connect(&poll_, &QTimer::timeout, this, [this] { pollInstances(); });
        poll_.start(30);
        if (selfTest_)
            QTimer::singleShot(10000, this, [this] {
                if (!finished_)
                {
                    failed_ = true;
                    std::fprintf(stderr, "Qt host self-test timed out\n");
                    logEvent("self-test timed out");
                    if (GetEnvironmentVariableA("VIM_RUNTIME_DEBUGBREAK", nullptr, 0) != 0)
                        DebugBreak();
                    requestClose();
                    QTimer::singleShot(2000, this, [] { QCoreApplication::exit(1); });
                }
            });
    }

    ~VimHost() override
    {
        if (selfTestLog_ != nullptr)
            std::fclose(selfTestLog_);
    }

    bool failed() const { return failed_; }

protected:
    void closeEvent(QCloseEvent *event) override
    {
        if (!allExited())
        {
            // A previous close may have been cancelled in Vim's save prompt.
            // Retry only on a new host close, not on every polling tick.
            closePosted_.fill(false);
            requestClose();
            event->ignore();
            return;
        }
        event->accept();
    }

private:
    std::string selfTestPath(const char *name) const
    {
        return selfTestDirectory_ + "/" + name;
    }

    void logEvent(const char *event)
    {
        if (selfTestLog_ != nullptr)
        {
            std::fprintf(selfTestLog_, "%s\n", event);
            std::fflush(selfTestLog_);
        }
    }

    void requestClose()
    {
        closing_ = true;
        for (std::size_t index = 0; index < instances_.size(); ++index)
            postClose(index);
    }

    void postClose(std::size_t index)
    {
        if (instances_[index] != nullptr && !closePosted_[index]
            && vim_runtime_instance_request_close(instances_[index]) == 1)
        {
            closePosted_[index] = true;
            logEvent(index == 0 ? "close posted A" : "close posted B");
        }
    }

    bool allExited() const
    {
        for (auto *instance : instances_)
            if (instance != nullptr)
                return false;
        return true;
    }

    void pollInstances()
    {
        for (std::size_t index = 0; index < instances_.size(); ++index)
        {
            auto *instance = instances_[index];
            if (instance == nullptr)
                continue;

            if (containers_[index] == nullptr)
            {
                if (void *native = vim_runtime_instance_window(instance))
                {
                    const HWND nativeParent = GetAncestor(
                        static_cast<HWND>(native), GA_PARENT);
                    if (nativeParent != parentWindows_[index])
                    {
                        failed_ = true;
                        if (!parentErrorLogged_[index])
                        {
                            parentErrorLogged_[index] = true;
                            std::fprintf(stderr,
                                         "Vim instance %zu was not embedded at startup (expected %p, actual %p)\n",
                                         index + 1, parentWindows_[index], nativeParent);
                        }
                        continue;
                    }
                    auto *window = QWindow::fromWinId(
                        static_cast<WId>(reinterpret_cast<quintptr>(native)));
                    if (window != nullptr)
                    {
                        auto *container = QWidget::createWindowContainer(window, this);
                        container->setFocusPolicy(Qt::StrongFocus);
                        container->setMinimumSize(320, 240);
                        layout_->replaceWidget(placeholders_[index], container);
                        layout_->setStretch(static_cast<int>(index), 1);
                        container->show();
                        placeholders_[index]->deleteLater();
                        placeholders_[index] = nullptr;
                        containers_[index] = container;
                        nativeWindows_[index] = static_cast<HWND>(native);
                        logEvent(index == 0 ? "attached A" : "attached B");
                    }
                }
            }

            int status = 0;
            if (vim_runtime_instance_wait(instance, 0, &status) == 1)
            {
                if (status != 0)
                {
                    failed_ = true;
                    std::fprintf(stderr, "Vim instance %zu exited with %d\n",
                                 index + 1, status);
                }
                if (vim_runtime_instance_destroy(instance) != 1)
                    failed_ = true;
                else if (selfTest_ && pythonTest_ && index == 0)
                {
                    std::FILE *marker = nullptr;
                    const auto path = selfTestPath("vim-qt-probe-A.destroyed");
                    if (fopen_s(&marker, path.c_str(), "w") != 0 || marker == nullptr)
                        failed_ = true;
                    else
                    {
                        std::fputs("A\n", marker);
                        std::fclose(marker);
                    }
                }
                instances_[index] = nullptr;
                nativeWindows_[index] = nullptr;
                if (containers_[index] != nullptr)
                {
                    auto *placeholder = new QLabel(QStringLiteral("Vim 已退出"), this);
                    placeholder->setAlignment(Qt::AlignCenter);
                    layout_->replaceWidget(containers_[index], placeholder);
                    containers_[index]->deleteLater();
                    containers_[index] = nullptr;
                    placeholders_[index] = placeholder;
                }
                logEvent(index == 0 ? "exited A" : "exited B");
            }
        }

        if (selfTest_ && !selfTestClosing_ && containers_[0] && containers_[1])
        {
            selfTestClosing_ = true;
            char hostGeometry[80];
            std::snprintf(hostGeometry, sizeof(hostGeometry),
                          "host %dx%d", width(), height());
            logEvent(hostGeometry);
            for (std::size_t index = 0; index < containers_.size(); ++index)
            {
                RECT outer{};
                RECT client{};
                RECT textArea{};
                GetWindowRect(nativeWindows_[index], &outer);
                GetClientRect(nativeWindows_[index], &client);
                const HWND textWindow = FindWindowExW(nativeWindows_[index],
                                                      nullptr, L"VimTextArea", nullptr);
                if (textWindow != nullptr)
                    GetClientRect(textWindow, &textArea);
                char geometry[160];
                std::snprintf(geometry, sizeof(geometry),
                              "%c: pane %dx%d, native %dx%d, client %dx%d, text %dx%d",
                              index == 0 ? 'A' : 'B',
                              containers_[index]->width(), containers_[index]->height(),
                              outer.right - outer.left, outer.bottom - outer.top,
                              client.right - client.left, client.bottom - client.top,
                              textArea.right - textArea.left,
                              textArea.bottom - textArea.top);
                logEvent(geometry);
            }
            QTimer::singleShot(2200, this, [this] {
                if (closeRetryTest_)
                {
                    close();
                    QTimer::singleShot(500, this, [this] {
                        for (std::size_t i = 0; i < instances_.size(); ++i)
                        {
                            if (instances_[i] == nullptr)
                                failed_ = true;
                            const auto cancelledPath = selfTestPath(i == 0
                                ? "vim-qt-probe-A.cancelled" : "vim-qt-probe-B.cancelled");
                            if (GetFileAttributesA(cancelledPath.c_str()) == INVALID_FILE_ATTRIBUTES)
                                failed_ = true;
                            if (nativeWindows_[i] != nullptr)
                                PostMessageW(nativeWindows_[i], WM_CHAR, '\r', 1);
                        }
                        logEvent("retrying cancelled close");
                        closeRetryObserved_ = true;
                        QTimer::singleShot(150, this, [this] { close(); });
                    });
                }
                else if (pythonTest_ && pythonQuitMode_.empty())
                    postClose(0);
                else if (!pythonTest_)
                    requestClose();
            });
        }

        if (selfTest_ && pythonTest_ && selfTestClosing_
            && instances_[0] == nullptr && instances_[1] != nullptr
            && GetFileAttributesA(selfTestPath("vim-qt-probe-B.after-a").c_str())
                != INVALID_FILE_ATTRIBUTES)
            postClose(1);

        if (closing_)
            requestClose();

        if (allExited() && !finished_)
        {
            finished_ = true;
            if (closeRetryTest_ && !closeRetryObserved_)
                failed_ = true;
            if (selfTest_)
            {
                for (const char *path : {"vim-qt-gui-dialog-A.log",
                                         "vim-qt-gui-dialog-B.log"})
                {
                    const std::string absolutePath = selfTestPath(path);
                    WIN32_FILE_ATTRIBUTE_DATA fileAttributes{};
                    if (GetFileAttributesExA(absolutePath.c_str(), GetFileExInfoStandard,
                                             &fileAttributes)
                        && (fileAttributes.nFileSizeLow != 0
                            || fileAttributes.nFileSizeHigh != 0))
                    {
                        failed_ = true;
                        std::fprintf(stderr, "Vim reported a GUI error in %s\n", path);
                    }
                }
                for (const char *name : {"A", "B"})
                {
                    char resultName[32];
                    std::snprintf(resultName, sizeof(resultName),
                                  "vim-qt-probe-%s.result", name);
                    const std::string resultPath = selfTestPath(resultName);
                    std::FILE *result = nullptr;
                    char marker[16]{};
                    char windows[16]{};
                    char rows[16]{};
                    char columns[16]{};
                    char error[256]{};
                    int rowCount = 0;
                    int columnCount = 0;
                    if (fopen_s(&result, resultPath.c_str(), "r") != 0
                        || result == nullptr
                        || std::fgets(marker, sizeof(marker), result) == nullptr
                        || std::fgets(windows, sizeof(windows), result) == nullptr
                        || std::fgets(rows, sizeof(rows), result) == nullptr
                        || std::fgets(columns, sizeof(columns), result) == nullptr
                        || std::fgets(error, sizeof(error), result) == nullptr
                        || marker[0] != name[0] || marker[1] != '\n'
                        || std::strcmp(windows, "2\n") != 0
                        || sscanf_s(rows, "%d", &rowCount) != 1
                        || rowCount < 4
                        || sscanf_s(columns, "%d", &columnCount) != 1
                        || columnCount < 20
                        || std::strcmp(error, "\n") != 0)
                    {
                        failed_ = true;
                        std::fprintf(stderr, "Vim GUI probe failed for %s\n", name);
                    }
                    if (result != nullptr)
                        std::fclose(result);
                    if (pythonTest_)
                    {
                        const std::string pythonPath = selfTestPath(
                            name[0] == 'A' ? "vim-qt-probe-A.python"
                                           : "vim-qt-probe-B.python");
                        std::FILE *pythonResult = nullptr;
                        char pythonMarker[16]{};
                        if (fopen_s(&pythonResult, pythonPath.c_str(), "r") != 0
                            || pythonResult == nullptr
                            || std::fgets(pythonMarker, sizeof(pythonMarker),
                                          pythonResult) == nullptr
                            || pythonMarker[0] != name[0]
                            || pythonMarker[1] != '\n')
                        {
                            failed_ = true;
                            std::fprintf(stderr,
                                         "Vim Python probe failed for %s\n", name);
                        }
                        if (pythonResult != nullptr)
                            std::fclose(pythonResult);
                    }
                }
                if (pythonTest_)
                {
                    if (GetFileAttributesA(selfTestPath("vim-qt-probe-A.leave").c_str()) == INVALID_FILE_ATTRIBUTES)
                    {
                        failed_ = true;
                        std::fprintf(stderr, "Vim A did not run its leave hook\n");
                    }
                    if (!pythonQuitMode_.empty()
                        && GetFileAttributesA(selfTestPath("vim-qt-probe-A.finally").c_str()) == INVALID_FILE_ATTRIBUTES)
                    {
                        failed_ = true;
                        std::fprintf(stderr, "Python exit skipped its finally block\n");
                    }
                    const std::string afterAPath = selfTestPath("vim-qt-probe-B.after-a");
                    std::FILE *afterA = nullptr;
                    char marker[16]{};
                    if (fopen_s(&afterA, afterAPath.c_str(), "r") != 0
                        || afterA == nullptr
                        || std::fgets(marker, sizeof(marker), afterA) == nullptr
                        || std::strcmp(marker, "B\n") != 0)
                    {
                        failed_ = true;
                        std::fprintf(stderr,
                                     "Vim B did not run Python after Vim A exited\n");
                    }
                    if (afterA != nullptr)
                        std::fclose(afterA);
                }
            }
            logEvent("all exited");
            poll_.stop();
            close();
        }
    }

    QHBoxLayout *layout_ = nullptr;
    QTimer poll_;
    std::array<vim_runtime_instance *, 2> instances_{};
    std::array<QLabel *, 2> placeholders_{};
    std::array<QWidget *, 2> containers_{};
    std::array<HWND, 2> nativeWindows_{};
    std::array<HWND, 2> parentWindows_{};
    std::array<bool, 2> parentErrorLogged_{};
    std::array<bool, 2> closePosted_{};
    bool selfTest_ = false;
    bool pythonTest_ = false;
    bool closeRetryTest_ = false;
    bool closeRetryObserved_ = false;
    std::string pythonQuitMode_;
    bool selfTestClosing_ = false;
    bool closing_ = false;
    bool finished_ = false;
    bool failed_ = false;
    std::FILE *selfTestLog_ = nullptr;
    std::string selfTestDirectory_;
};

} // namespace

int main(int argc, char **argv)
{
    QApplication app(argc, argv);
    bool selfTest = false;
    bool pythonTest = false;
    bool closeRetryTest = false;
    std::string pythonQuitMode;
    for (int index = 1; index < argc; ++index)
        if (QString::fromLocal8Bit(argv[index]) == QStringLiteral("--self-test"))
            selfTest = true;
        else if (QString::fromLocal8Bit(argv[index])
                 == QStringLiteral("--self-test-python"))
        {
            selfTest = true;
            pythonTest = true;
        }
        else if (QString::fromLocal8Bit(argv[index])
                 == QStringLiteral("--self-test-close-retry"))
        {
            selfTest = true;
            closeRetryTest = true;
        }
        else if (QString::fromLocal8Bit(argv[index]).startsWith(
                     QStringLiteral("--self-test-python-quit=")))
        {
            selfTest = true;
            pythonTest = true;
            pythonQuitMode = argv[index] + std::strlen("--self-test-python-quit=");
        }

    VimHost host(selfTest, pythonTest, closeRetryTest, std::move(pythonQuitMode));
    host.show();
    const int result = app.exec();
    return host.failed() ? 1 : result;
}
