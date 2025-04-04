" Name:         unokai
" Description:  Color scheme similar to Monokai originally created by Wimer Hazenberg for TextMate
" Author:       k-37 <60838818+k-37@users.noreply.github.com>
" Maintainer:   k-37 <60838818+k-37@users.noreply.github.com>
" Website:      https://github.com/vim/colorschemes
" License:      Vim License (see `:help license`)
" Last Change:  2024 Dec 15

" Generated by Colortemplate v2.2.3

set background=dark

hi clear
let g:colors_name = 'unokai'

let s:t_Co = has('gui_running') ? -1 : (&t_Co ?? 0)
let s:italics = has('gui_running') || (&t_ZH != '' && &t_ZH != '[7m' && !has('win32'))

if (has('termguicolors') && &termguicolors) || has('gui_running')
  let g:terminal_ansi_colors = ['#282923', '#c61e5c', '#81af24', '#fd971f', '#51aebe', '#ae81ff', '#80beb5', '#bababa', '#74705d', '#f92672', '#a6e22e', '#e6db74', '#66d9ef', '#fd5ff0', '#a1efe4', '#f8f8f2']
endif
hi! link CursorLineFold FoldColumn
hi! link CursorLineSign SignColumn
hi! link MessageWindow Pmenu
hi! link PopupNotification Todo
hi! link PopupSelected PmenuSel
hi! link StatusLineTerm StatusLine
hi! link StatusLineTermNC StatusLineNC
hi! link Terminal Normal
hi! link Delimiter PreProc
hi! link Operator PreProc
hi! link StorageClass PreProc
hi! link Structure PreProc
hi! link Define Identifier
hi! link Label String
hi! link markdownCode Comment
hi! link markdownCodeBlock markdownCode
hi! link markdownCodeDelimiter markdownCode
hi Normal guifg=#f8f8f2 guibg=#282923 gui=NONE cterm=NONE
hi StatusLine guifg=#282923 guibg=#bababa gui=NONE cterm=NONE
hi StatusLineNC guifg=#282923 guibg=#74705d gui=NONE cterm=NONE
hi VertSplit guifg=#74705d guibg=#74705d gui=NONE cterm=NONE
hi TabLine guifg=#282923 guibg=#74705d gui=NONE cterm=NONE
hi TabLineFill guifg=#282923 guibg=#74705d gui=NONE cterm=NONE
hi TabLineSel guifg=#282923 guibg=#bababa gui=bold cterm=bold
hi ToolbarLine guifg=NONE guibg=NONE gui=NONE ctermfg=NONE ctermbg=NONE cterm=NONE
hi ToolbarButton guifg=#74705d guibg=#f8f8f2 gui=bold,reverse cterm=bold,reverse
hi QuickFixLine guifg=#282923 guibg=#51aebe gui=NONE cterm=NONE
hi CursorLineNr guifg=#dadada guibg=NONE gui=bold cterm=bold
hi LineNr guifg=#8a8a8a guibg=NONE gui=NONE cterm=NONE
hi LineNrAbove guifg=#8a8a8a guibg=NONE gui=NONE cterm=NONE
hi LineNrBelow guifg=#8a8a8a guibg=NONE gui=NONE cterm=NONE
hi NonText guifg=#8a8a8a guibg=NONE gui=NONE cterm=NONE
hi EndOfBuffer guifg=#8a8a8a guibg=NONE gui=NONE cterm=NONE
hi SpecialKey guifg=#8a8a8a guibg=NONE gui=NONE cterm=NONE
hi FoldColumn guifg=#8a8a8a guibg=NONE gui=NONE cterm=NONE
hi Visual guifg=#a1efe4 guibg=#282923 gui=reverse cterm=reverse
hi VisualNOS guifg=#282923 guibg=#80beb5 gui=NONE cterm=NONE
hi Pmenu guifg=NONE guibg=#585858 gui=NONE cterm=NONE
hi PmenuThumb guifg=NONE guibg=#74705d gui=NONE cterm=NONE
hi PmenuSbar guifg=NONE guibg=NONE gui=NONE ctermfg=NONE ctermbg=NONE cterm=NONE
hi PmenuSel guifg=NONE guibg=#8a8a8a gui=NONE cterm=NONE
hi PmenuKind guifg=#80beb5 guibg=#585858 gui=NONE cterm=NONE
hi PmenuKindSel guifg=#80beb5 guibg=#8a8a8a gui=NONE cterm=NONE
hi PmenuExtra guifg=#bababa guibg=#585858 gui=NONE cterm=NONE
hi PmenuExtraSel guifg=#bababa guibg=#8a8a8a gui=NONE cterm=NONE
hi PmenuMatch guifg=#ffaf5f guibg=#585858 gui=NONE cterm=NONE
hi PmenuMatchSel guifg=#ffaf5f guibg=#8a8a8a gui=NONE cterm=NONE
hi SignColumn guifg=NONE guibg=NONE gui=NONE ctermfg=NONE ctermbg=NONE cterm=NONE
hi Error guifg=#f92672 guibg=#000000 gui=reverse cterm=reverse
hi ErrorMsg guifg=#f92672 guibg=#000000 gui=reverse cterm=reverse
hi ModeMsg guifg=NONE guibg=NONE gui=bold ctermfg=NONE ctermbg=NONE cterm=bold
hi MoreMsg guifg=#81af24 guibg=NONE gui=NONE cterm=NONE
hi Question guifg=#e6db74 guibg=NONE gui=NONE cterm=NONE
hi WarningMsg guifg=#f92672 guibg=NONE gui=NONE cterm=NONE
hi Todo guifg=#dadada guibg=NONE gui=bold cterm=bold
hi MatchParen guifg=#fd971f guibg=NONE gui=bold cterm=bold
hi Search guifg=#66d9ef guibg=#282923 gui=reverse cterm=reverse
hi IncSearch guifg=#ffaf5f guibg=#282923 gui=reverse cterm=reverse
hi CurSearch guifg=#ffaf5f guibg=#282923 gui=reverse cterm=reverse
hi WildMenu guifg=#282923 guibg=#e6db74 gui=bold cterm=bold
hi debugPC guifg=#282923 guibg=#51aebe gui=NONE cterm=NONE
hi debugBreakpoint guifg=#282923 guibg=#f92672 gui=NONE cterm=NONE
hi Cursor guifg=#000000 guibg=#dadada gui=NONE cterm=NONE
hi lCursor guifg=#282923 guibg=#5fff00 gui=NONE cterm=NONE
hi CursorLine guifg=NONE guibg=#3a392f gui=NONE cterm=NONE
hi CursorColumn guifg=NONE guibg=#3a392f gui=NONE cterm=NONE
hi Folded guifg=#bababa guibg=#414141 gui=NONE cterm=NONE
hi ColorColumn guifg=NONE guibg=#585858 gui=NONE cterm=NONE
hi SpellBad guifg=NONE guibg=NONE guisp=#d75f5f gui=undercurl ctermfg=NONE ctermbg=NONE cterm=underline
hi SpellCap guifg=NONE guibg=NONE guisp=#ffaf5f gui=undercurl ctermfg=NONE ctermbg=NONE cterm=underline
hi SpellLocal guifg=NONE guibg=NONE guisp=#5fd75f gui=undercurl ctermfg=NONE ctermbg=NONE cterm=underline
hi SpellRare guifg=NONE guibg=NONE guisp=#fd5ff0 gui=undercurl ctermfg=NONE ctermbg=NONE cterm=underline
hi Constant guifg=#ae81ff guibg=NONE gui=NONE cterm=NONE
hi Type guifg=#fd971f guibg=NONE gui=bold cterm=bold
hi Character guifg=#a6e22e guibg=NONE gui=NONE cterm=NONE
hi Comment guifg=#74705d guibg=NONE gui=NONE cterm=NONE
hi String guifg=#e6db74 guibg=NONE gui=NONE cterm=NONE
hi Function guifg=#a6e22e guibg=NONE gui=NONE cterm=NONE
hi Identifier guifg=#66d9ef guibg=NONE gui=NONE cterm=NONE
hi PreProc guifg=#f92672 guibg=NONE gui=NONE cterm=NONE
hi Special guifg=#80beb5 guibg=NONE gui=NONE cterm=NONE
hi Statement guifg=#f92672 guibg=NONE gui=bold cterm=bold
hi Underlined guifg=#66d9ef guibg=NONE gui=underline cterm=underline
hi Title guifg=NONE guibg=NONE gui=bold ctermfg=NONE ctermbg=NONE cterm=bold
hi Debug guifg=#80beb5 guibg=NONE gui=NONE cterm=NONE
hi Ignore guifg=NONE guibg=NONE gui=NONE ctermfg=NONE ctermbg=NONE cterm=NONE
hi Directory guifg=#a1efe4 guibg=NONE gui=bold cterm=bold
hi Conceal guifg=#8a8a8a guibg=NONE gui=NONE cterm=NONE
hi DiffAdd guifg=#5faf5f guibg=NONE gui=reverse cterm=reverse
hi DiffChange guifg=#5f87af guibg=NONE gui=reverse cterm=reverse
hi DiffText guifg=#af87af guibg=NONE gui=reverse cterm=reverse
hi DiffDelete guifg=#af5f5f guibg=NONE gui=reverse cterm=reverse
hi Added guifg=#5fd75f guibg=NONE gui=NONE cterm=NONE
hi Changed guifg=#ffaf5f guibg=NONE gui=NONE cterm=NONE
hi Removed guifg=#d75f5f guibg=NONE gui=NONE cterm=NONE
hi htmlBold guifg=#f8f8f2 guibg=NONE gui=bold cterm=bold
hi htmlItalic guifg=#f8f8f2 guibg=NONE gui=italic cterm=italic
hi markdownHeadingDelimiter guifg=#f8f8f2 guibg=NONE gui=NONE cterm=NONE
hi markdownH1Delimiter guifg=#f92672 guibg=NONE gui=NONE cterm=NONE
hi markdownH2Delimiter guifg=#e6db74 guibg=NONE gui=NONE cterm=NONE
hi markdownH4Delimiter guifg=#66d9ef guibg=NONE gui=NONE cterm=NONE
hi markdownH6Delimiter guifg=#a6e22e guibg=NONE gui=NONE cterm=NONE
hi markdownH3Delimiter guifg=#fd971f guibg=NONE gui=NONE cterm=NONE
hi markdownH5Delimiter guifg=#51aebe guibg=NONE gui=NONE cterm=NONE
if !s:italics
  hi htmlItalic gui=NONE cterm=NONE
endif

if s:t_Co >= 256
  hi! link CursorLineFold FoldColumn
  hi! link CursorLineSign SignColumn
  hi! link MessageWindow Pmenu
  hi! link PopupNotification Todo
  hi! link PopupSelected PmenuSel
  hi! link StatusLineTerm StatusLine
  hi! link StatusLineTermNC StatusLineNC
  hi! link Terminal Normal
  hi! link Delimiter PreProc
  hi! link Operator PreProc
  hi! link StorageClass PreProc
  hi! link Structure PreProc
  hi! link Define Identifier
  hi! link Label String
  hi! link markdownCode Comment
  hi! link markdownCodeBlock markdownCode
  hi! link markdownCodeDelimiter markdownCode
  hi Normal ctermfg=255 ctermbg=235 cterm=NONE
  hi StatusLine ctermfg=235 ctermbg=250 cterm=NONE
  hi StatusLineNC ctermfg=235 ctermbg=244 cterm=NONE
  hi VertSplit ctermfg=244 ctermbg=244 cterm=NONE
  hi TabLine ctermfg=235 ctermbg=244 cterm=NONE
  hi TabLineFill ctermfg=235 ctermbg=244 cterm=NONE
  hi TabLineSel ctermfg=235 ctermbg=250 cterm=bold
  hi ToolbarLine ctermfg=NONE ctermbg=NONE cterm=NONE
  hi ToolbarButton ctermfg=244 ctermbg=255 cterm=bold,reverse
  hi QuickFixLine ctermfg=235 ctermbg=141 cterm=NONE
  hi CursorLineNr ctermfg=253 ctermbg=NONE cterm=bold
  hi LineNr ctermfg=245 ctermbg=NONE cterm=NONE
  hi LineNrAbove ctermfg=245 ctermbg=NONE cterm=NONE
  hi LineNrBelow ctermfg=245 ctermbg=NONE cterm=NONE
  hi NonText ctermfg=245 ctermbg=NONE cterm=NONE
  hi EndOfBuffer ctermfg=245 ctermbg=NONE cterm=NONE
  hi SpecialKey ctermfg=245 ctermbg=NONE cterm=NONE
  hi FoldColumn ctermfg=245 ctermbg=NONE cterm=NONE
  hi Visual ctermfg=116 ctermbg=235 cterm=reverse
  hi VisualNOS ctermfg=235 ctermbg=73 cterm=NONE
  hi Pmenu ctermfg=NONE ctermbg=240 cterm=NONE
  hi PmenuThumb ctermfg=NONE ctermbg=244 cterm=NONE
  hi PmenuSbar ctermfg=NONE ctermbg=NONE cterm=NONE
  hi PmenuSel ctermfg=NONE ctermbg=245 cterm=NONE
  hi PmenuKind ctermfg=73 ctermbg=240 cterm=NONE
  hi PmenuKindSel ctermfg=73 ctermbg=245 cterm=NONE
  hi PmenuExtra ctermfg=250 ctermbg=240 cterm=NONE
  hi PmenuExtraSel ctermfg=250 ctermbg=245 cterm=NONE
  hi PmenuMatch ctermfg=215 ctermbg=240 cterm=NONE
  hi PmenuMatchSel ctermfg=215 ctermbg=245 cterm=NONE
  hi SignColumn ctermfg=NONE ctermbg=NONE cterm=NONE
  hi Error ctermfg=197 ctermbg=16 cterm=reverse
  hi ErrorMsg ctermfg=197 ctermbg=16 cterm=reverse
  hi ModeMsg ctermfg=NONE ctermbg=NONE cterm=bold
  hi MoreMsg ctermfg=106 ctermbg=NONE cterm=NONE
  hi Question ctermfg=185 ctermbg=NONE cterm=NONE
  hi WarningMsg ctermfg=197 ctermbg=NONE cterm=NONE
  hi Todo ctermfg=253 ctermbg=NONE cterm=bold
  hi MatchParen ctermfg=208 ctermbg=NONE cterm=bold
  hi Search ctermfg=81 ctermbg=235 cterm=reverse
  hi IncSearch ctermfg=215 ctermbg=235 cterm=reverse
  hi CurSearch ctermfg=215 ctermbg=235 cterm=reverse
  hi WildMenu ctermfg=235 ctermbg=185 cterm=bold
  hi debugPC ctermfg=235 ctermbg=73 cterm=NONE
  hi debugBreakpoint ctermfg=235 ctermbg=197 cterm=NONE
  hi CursorLine ctermfg=NONE ctermbg=237 cterm=NONE
  hi CursorColumn ctermfg=NONE ctermbg=237 cterm=NONE
  hi Folded ctermfg=250 ctermbg=238 cterm=NONE
  hi ColorColumn ctermfg=NONE ctermbg=240 cterm=NONE
  hi SpellBad ctermfg=167 ctermbg=NONE cterm=underline
  hi SpellCap ctermfg=215 ctermbg=NONE cterm=underline
  hi SpellLocal ctermfg=77 ctermbg=NONE cterm=underline
  hi SpellRare ctermfg=207 ctermbg=NONE cterm=underline
  hi Constant ctermfg=141 ctermbg=NONE cterm=NONE
  hi Type ctermfg=208 ctermbg=NONE cterm=bold
  hi Character ctermfg=112 ctermbg=NONE cterm=NONE
  hi Comment ctermfg=244 ctermbg=NONE cterm=NONE
  hi String ctermfg=185 ctermbg=NONE cterm=NONE
  hi Function ctermfg=112 ctermbg=NONE cterm=NONE
  hi Identifier ctermfg=81 ctermbg=NONE cterm=NONE
  hi PreProc ctermfg=197 ctermbg=NONE cterm=NONE
  hi Special ctermfg=73 ctermbg=NONE cterm=NONE
  hi Statement ctermfg=197 ctermbg=NONE cterm=bold
  hi Underlined ctermfg=81 ctermbg=NONE cterm=underline
  hi Title ctermfg=NONE ctermbg=NONE cterm=bold
  hi Debug ctermfg=73 ctermbg=NONE cterm=NONE
  hi Ignore ctermfg=NONE ctermbg=NONE cterm=NONE
  hi Directory ctermfg=116 ctermbg=NONE cterm=bold
  hi Conceal ctermfg=245 ctermbg=NONE cterm=NONE
  hi DiffAdd ctermfg=71 ctermbg=NONE cterm=reverse
  hi DiffChange ctermfg=67 ctermbg=NONE cterm=reverse
  hi DiffText ctermfg=139 ctermbg=NONE cterm=reverse
  hi DiffDelete ctermfg=131 ctermbg=NONE cterm=reverse
  hi Added ctermfg=77 ctermbg=NONE cterm=NONE
  hi Changed ctermfg=215 ctermbg=NONE cterm=NONE
  hi Removed ctermfg=167 ctermbg=NONE cterm=NONE
  hi htmlBold ctermfg=255 ctermbg=NONE cterm=bold
  hi htmlItalic ctermfg=255 ctermbg=NONE cterm=underline
  hi markdownHeadingDelimiter ctermfg=255 ctermbg=NONE cterm=NONE
  hi markdownH1Delimiter ctermfg=197 ctermbg=NONE cterm=NONE
  hi markdownH2Delimiter ctermfg=185 ctermbg=NONE cterm=NONE
  hi markdownH4Delimiter ctermfg=81 ctermbg=NONE cterm=NONE
  hi markdownH6Delimiter ctermfg=112 ctermbg=NONE cterm=NONE
  hi markdownH3Delimiter ctermfg=208 ctermbg=NONE cterm=NONE
  hi markdownH5Delimiter ctermfg=73 ctermbg=NONE cterm=NONE
  unlet s:t_Co s:italics
  finish
endif

if s:t_Co >= 16
  hi Normal ctermfg=white ctermbg=black cterm=NONE
  hi StatusLine ctermfg=black ctermbg=gray cterm=NONE
  hi StatusLineNC ctermfg=black ctermbg=darkgray cterm=NONE
  hi VertSplit ctermfg=darkgray ctermbg=darkgray cterm=NONE
  hi TabLine ctermfg=black ctermbg=darkgray cterm=NONE
  hi TabLineFill ctermfg=black ctermbg=darkgray cterm=NONE
  hi TabLineSel ctermfg=black ctermbg=gray cterm=bold
  hi ToolbarLine ctermfg=NONE ctermbg=NONE cterm=NONE
  hi ToolbarButton ctermfg=darkgray ctermbg=white cterm=bold,reverse
  hi QuickFixLine ctermfg=black ctermbg=darkmagenta cterm=NONE
  hi CursorLineNr ctermfg=white ctermbg=NONE cterm=bold
  hi LineNr ctermfg=darkgrey ctermbg=NONE cterm=NONE
  hi LineNrAbove ctermfg=darkgrey ctermbg=NONE cterm=NONE
  hi LineNrBelow ctermfg=darkgrey ctermbg=NONE cterm=NONE
  hi NonText ctermfg=darkgrey ctermbg=NONE cterm=NONE
  hi EndOfBuffer ctermfg=darkgrey ctermbg=NONE cterm=NONE
  hi SpecialKey ctermfg=darkgrey ctermbg=NONE cterm=NONE
  hi FoldColumn ctermfg=darkgrey ctermbg=NONE cterm=NONE
  hi Visual ctermfg=cyan ctermbg=black cterm=reverse
  hi VisualNOS ctermfg=black ctermbg=darkcyan cterm=NONE
  hi Pmenu ctermfg=black ctermbg=gray cterm=NONE
  hi PmenuThumb ctermfg=gray ctermbg=black cterm=NONE
  hi PmenuSbar ctermfg=NONE ctermbg=gray cterm=NONE
  hi PmenuSel ctermfg=black ctermbg=darkyellow cterm=NONE
  hi PmenuKind ctermfg=darkred ctermbg=gray cterm=NONE
  hi PmenuKindSel ctermfg=darkred ctermbg=darkyellow cterm=NONE
  hi PmenuExtra ctermfg=darkgray ctermbg=gray cterm=NONE
  hi PmenuExtraSel ctermfg=black ctermbg=darkyellow cterm=NONE
  hi PmenuMatch ctermfg=black ctermbg=gray cterm=bold
  hi PmenuMatchSel ctermfg=black ctermbg=darkyellow cterm=bold
  hi SignColumn ctermfg=NONE ctermbg=NONE cterm=NONE
  hi Error ctermfg=red ctermbg=black cterm=reverse
  hi ErrorMsg ctermfg=red ctermbg=black cterm=reverse
  hi ModeMsg ctermfg=NONE ctermbg=NONE cterm=bold
  hi MoreMsg ctermfg=darkgreen ctermbg=NONE cterm=NONE
  hi Question ctermfg=yellow ctermbg=NONE cterm=NONE
  hi WarningMsg ctermfg=red ctermbg=NONE cterm=NONE
  hi Todo ctermfg=white ctermbg=NONE cterm=bold
  hi MatchParen ctermfg=darkyellow ctermbg=NONE cterm=bold
  hi Search ctermfg=blue ctermbg=black cterm=reverse
  hi IncSearch ctermfg=red ctermbg=black cterm=reverse
  hi CurSearch ctermfg=red ctermbg=black cterm=reverse
  hi WildMenu ctermfg=black ctermbg=yellow cterm=bold
  hi debugPC ctermfg=black ctermbg=darkblue cterm=NONE
  hi debugBreakpoint ctermfg=black ctermbg=red cterm=NONE
  hi CursorLine ctermfg=NONE ctermbg=NONE cterm=underline
  hi CursorColumn ctermfg=black ctermbg=darkyellow cterm=NONE
  hi Folded ctermfg=black ctermbg=darkyellow cterm=NONE
  hi ColorColumn ctermfg=black ctermbg=darkyellow cterm=NONE
  hi SpellBad ctermfg=darkred ctermbg=NONE cterm=underline
  hi SpellCap ctermfg=darkyellow ctermbg=NONE cterm=underline
  hi SpellLocal ctermfg=darkgreen ctermbg=NONE cterm=underline
  hi SpellRare ctermfg=magenta ctermbg=NONE cterm=underline
  hi Constant ctermfg=darkmagenta ctermbg=NONE cterm=NONE
  hi Type ctermfg=darkyellow ctermbg=NONE cterm=bold
  hi Character ctermfg=green ctermbg=NONE cterm=NONE
  hi Comment ctermfg=darkgray ctermbg=NONE cterm=NONE
  hi String ctermfg=yellow ctermbg=NONE cterm=NONE
  hi Function ctermfg=green ctermbg=NONE cterm=NONE
  hi Identifier ctermfg=blue ctermbg=NONE cterm=NONE
  hi PreProc ctermfg=red ctermbg=NONE cterm=NONE
  hi Special ctermfg=darkcyan ctermbg=NONE cterm=NONE
  hi Statement ctermfg=red ctermbg=NONE cterm=bold
  hi Underlined ctermfg=blue ctermbg=NONE cterm=underline
  hi Title ctermfg=NONE ctermbg=NONE cterm=bold
  hi Debug ctermfg=darkcyan ctermbg=NONE cterm=NONE
  hi Ignore ctermfg=NONE ctermbg=NONE cterm=NONE
  hi Directory ctermfg=cyan ctermbg=NONE cterm=bold
  hi Conceal ctermfg=darkgrey ctermbg=NONE cterm=NONE
  hi DiffAdd ctermfg=darkgreen ctermbg=NONE cterm=reverse
  hi DiffChange ctermfg=darkblue ctermbg=NONE cterm=reverse
  hi DiffText ctermfg=darkmagenta ctermbg=NONE cterm=reverse
  hi DiffDelete ctermfg=darkred ctermbg=NONE cterm=reverse
  hi Added ctermfg=darkgreen ctermbg=NONE cterm=NONE
  hi Changed ctermfg=darkyellow ctermbg=NONE cterm=NONE
  hi Removed ctermfg=darkred ctermbg=NONE cterm=NONE
  hi htmlBold ctermfg=white ctermbg=NONE cterm=bold
  hi htmlItalic ctermfg=white ctermbg=NONE cterm=underline
  hi markdownHeadingDelimiter ctermfg=white ctermbg=NONE cterm=NONE
  hi markdownH1Delimiter ctermfg=red ctermbg=NONE cterm=NONE
  hi markdownH2Delimiter ctermfg=yellow ctermbg=NONE cterm=NONE
  hi markdownH4Delimiter ctermfg=blue ctermbg=NONE cterm=NONE
  hi markdownH6Delimiter ctermfg=green ctermbg=NONE cterm=NONE
  hi markdownH3Delimiter ctermfg=darkyellow ctermbg=NONE cterm=NONE
  hi markdownH5Delimiter ctermfg=darkblue ctermbg=NONE cterm=NONE
  unlet s:t_Co s:italics
  finish
endif

if s:t_Co >= 8
  hi Normal ctermfg=gray ctermbg=black cterm=NONE
  hi StatusLine ctermfg=gray ctermbg=black cterm=bold,reverse
  hi StatusLineNC ctermfg=gray ctermbg=black cterm=reverse
  hi VertSplit ctermfg=gray ctermbg=gray cterm=NONE
  hi TabLine ctermfg=black ctermbg=gray cterm=NONE
  hi TabLineFill ctermfg=gray ctermbg=gray cterm=NONE
  hi TabLineSel ctermfg=black ctermbg=gray cterm=bold
  hi ToolbarLine ctermfg=NONE ctermbg=NONE cterm=NONE
  hi ToolbarButton ctermfg=gray ctermbg=black cterm=reverse
  hi QuickFixLine ctermfg=black ctermbg=darkyellow cterm=NONE
  hi CursorLineNr ctermfg=darkyellow ctermbg=NONE cterm=bold
  hi LineNr ctermfg=gray ctermbg=NONE cterm=bold
  hi LineNrAbove ctermfg=gray ctermbg=NONE cterm=bold
  hi LineNrBelow ctermfg=gray ctermbg=NONE cterm=bold
  hi NonText ctermfg=gray ctermbg=NONE cterm=bold
  hi EndOfBuffer ctermfg=gray ctermbg=NONE cterm=bold
  hi SpecialKey ctermfg=gray ctermbg=NONE cterm=bold
  hi FoldColumn ctermfg=gray ctermbg=NONE cterm=bold
  hi Visual ctermfg=black ctermbg=darkcyan cterm=NONE
  hi VisualNOS ctermfg=black ctermbg=darkcyan cterm=NONE
  hi Pmenu ctermfg=black ctermbg=gray cterm=NONE
  hi PmenuThumb ctermfg=gray ctermbg=black cterm=NONE
  hi PmenuSbar ctermfg=NONE ctermbg=gray cterm=NONE
  hi PmenuSel ctermfg=black ctermbg=darkyellow cterm=NONE
  hi PmenuKind ctermfg=darkred ctermbg=gray cterm=NONE
  hi PmenuKindSel ctermfg=darkred ctermbg=darkyellow cterm=NONE
  hi PmenuExtra ctermfg=black ctermbg=gray cterm=NONE
  hi PmenuExtraSel ctermfg=black ctermbg=darkyellow cterm=NONE
  hi PmenuMatch ctermfg=black ctermbg=gray cterm=bold
  hi PmenuMatchSel ctermfg=black ctermbg=darkyellow cterm=bold
  hi SignColumn ctermfg=NONE ctermbg=NONE cterm=NONE
  hi Error ctermfg=darkred ctermbg=gray cterm=bold,reverse
  hi ErrorMsg ctermfg=darkred ctermbg=gray cterm=bold,reverse
  hi ModeMsg ctermfg=NONE ctermbg=NONE cterm=bold
  hi MoreMsg ctermfg=darkgreen ctermbg=NONE cterm=NONE
  hi Question ctermfg=darkyellow ctermbg=NONE cterm=NONE
  hi WarningMsg ctermfg=darkred ctermbg=NONE cterm=NONE
  hi Todo ctermfg=gray ctermbg=NONE cterm=bold
  hi MatchParen ctermfg=darkyellow ctermbg=NONE cterm=bold
  hi Search ctermfg=black ctermbg=darkblue cterm=NONE
  hi IncSearch ctermfg=black ctermbg=darkyellow cterm=NONE
  hi CurSearch ctermfg=black ctermbg=darkyellow cterm=NONE
  hi WildMenu ctermfg=black ctermbg=darkyellow cterm=NONE
  hi debugPC ctermfg=black ctermbg=darkblue cterm=NONE
  hi debugBreakpoint ctermfg=black ctermbg=darkcyan cterm=NONE
  hi CursorLine ctermfg=NONE ctermbg=NONE cterm=underline
  hi CursorColumn ctermfg=black ctermbg=darkyellow cterm=NONE
  hi Folded ctermfg=black ctermbg=darkyellow cterm=NONE
  hi ColorColumn ctermfg=black ctermbg=darkyellow cterm=NONE
  hi SpellBad ctermfg=darkred ctermbg=gray cterm=reverse
  hi SpellCap ctermfg=darkblue ctermbg=gray cterm=reverse
  hi SpellLocal ctermfg=darkgreen ctermbg=black cterm=reverse
  hi SpellRare ctermfg=darkmagenta ctermbg=gray cterm=reverse
  hi Constant ctermfg=darkmagenta ctermbg=NONE cterm=NONE
  hi Type ctermfg=darkyellow ctermbg=NONE cterm=bold
  hi Character ctermfg=darkgreen ctermbg=NONE cterm=NONE
  hi Comment ctermfg=gray ctermbg=NONE cterm=bold
  hi String ctermfg=darkyellow ctermbg=NONE cterm=bold
  hi Function ctermfg=darkgreen ctermbg=NONE cterm=NONE
  hi Identifier ctermfg=darkblue ctermbg=NONE cterm=NONE
  hi PreProc ctermfg=darkred ctermbg=NONE cterm=NONE
  hi Special ctermfg=darkcyan ctermbg=NONE cterm=bold
  hi Statement ctermfg=darkred ctermbg=NONE cterm=bold
  hi Underlined ctermfg=darkblue ctermbg=NONE cterm=underline
  hi Title ctermfg=NONE ctermbg=NONE cterm=bold
  hi Debug ctermfg=darkcyan ctermbg=NONE cterm=NONE
  hi Ignore ctermfg=NONE ctermbg=NONE cterm=NONE
  hi Directory ctermfg=darkcyan ctermbg=NONE cterm=bold
  hi Conceal ctermfg=gray ctermbg=NONE cterm=NONE
  hi DiffAdd ctermfg=darkgreen ctermbg=NONE cterm=reverse
  hi DiffChange ctermfg=darkblue ctermbg=NONE cterm=reverse
  hi DiffText ctermfg=darkmagenta ctermbg=NONE cterm=reverse
  hi DiffDelete ctermfg=darkred ctermbg=NONE cterm=reverse
  hi Added ctermfg=darkgreen ctermbg=NONE cterm=NONE
  hi Changed ctermfg=darkyellow ctermbg=NONE cterm=NONE
  hi Removed ctermfg=darkred ctermbg=NONE cterm=NONE
  hi htmlBold ctermfg=gray ctermbg=NONE cterm=bold
  hi htmlItalic ctermfg=gray ctermbg=NONE cterm=underline
  hi markdownHeadingDelimiter ctermfg=gray ctermbg=NONE cterm=NONE
  hi markdownH1Delimiter ctermfg=darkred ctermbg=NONE cterm=NONE
  hi markdownH2Delimiter ctermfg=darkyellow ctermbg=NONE cterm=NONE
  hi markdownH4Delimiter ctermfg=darkblue ctermbg=NONE cterm=NONE
  hi markdownH6Delimiter ctermfg=darkgreen ctermbg=NONE cterm=NONE
  hi markdownH3Delimiter ctermfg=darkyellow ctermbg=NONE cterm=NONE
  hi markdownH5Delimiter ctermfg=darkblue ctermbg=NONE cterm=NONE
  unlet s:t_Co s:italics
  finish
endif

if s:t_Co >= 0
  hi Normal term=NONE
  hi ColorColumn term=reverse
  hi Conceal term=NONE
  hi Cursor term=reverse
  hi CursorColumn term=NONE
  hi CursorLine term=underline
  hi CursorLineNr term=bold
  hi DiffAdd term=reverse
  hi DiffChange term=NONE
  hi DiffDelete term=reverse
  hi DiffText term=reverse
  hi Directory term=NONE
  hi EndOfBuffer term=NONE
  hi ErrorMsg term=bold,reverse
  hi FoldColumn term=NONE
  hi Folded term=NONE
  hi IncSearch term=bold,reverse,underline
  hi LineNr term=NONE
  hi MatchParen term=bold,underline
  hi ModeMsg term=bold
  hi MoreMsg term=NONE
  hi NonText term=NONE
  hi Pmenu term=reverse
  hi PmenuSbar term=reverse
  hi PmenuSel term=bold
  hi PmenuThumb term=NONE
  hi Question term=standout
  hi Search term=reverse
  hi SignColumn term=reverse
  hi SpecialKey term=bold
  hi SpellBad term=underline
  hi SpellCap term=underline
  hi SpellLocal term=underline
  hi SpellRare term=underline
  hi StatusLine term=bold,reverse
  hi StatusLineNC term=bold,underline
  hi TabLine term=bold,underline
  hi TabLineFill term=NONE
  hi Terminal term=NONE
  hi TabLineSel term=bold,reverse
  hi Title term=NONE
  hi VertSplit term=NONE
  hi Visual term=reverse
  hi VisualNOS term=NONE
  hi WarningMsg term=standout
  hi WildMenu term=bold
  hi CursorIM term=NONE
  hi ToolbarLine term=reverse
  hi ToolbarButton term=bold,reverse
  hi CurSearch term=reverse
  hi CursorLineFold term=underline
  hi CursorLineSign term=underline
  hi Comment term=bold
  hi Constant term=NONE
  hi Error term=bold,reverse
  hi Identifier term=NONE
  hi Ignore term=NONE
  hi PreProc term=NONE
  hi Special term=NONE
  hi Statement term=NONE
  hi Todo term=bold,reverse
  hi Type term=NONE
  hi Underlined term=underline
  unlet s:t_Co s:italics
  finish
endif

" Background: dark
" Color: color00               #282923        235            black
" Color: color08               #74705d        244            darkgray
" Color: color01               #c61e5c        125            darkred
" Color: color09               #f92672        197            red
" Color: color02               #81af24        106            darkgreen
" Color: color10               #a6e22e        112            green
" Color: color03               #fd971f        208            darkyellow
" Color: color11               #e6db74        185            yellow
" Color: color04               #51aebe        73             darkblue
" Color: color12               #66d9ef        81             blue
" Color: color05               #ae81ff        141            darkmagenta
" Color: color13               #fd5ff0        207            magenta
" Color: color06               #80beb5        73             darkcyan
" Color: color14               #a1efe4        116            cyan
" Color: color07               #bababa        250            gray
" Color: color15               #f8f8f2        255            white
" Color: colorLine             #3a392f        237            darkgrey
" Color: colorB                #585858        240            darkgrey
" Color: colorF                #414141        238            darkgrey
" Color: colorNonT             #8a8a8a        245            darkgrey
" Color: colorC                #ffaf5f        215            red
" Color: colorlC               #5fff00        82             green
" Color: colorV                #1f3f5f        109            cyan
" Color: colorMP               #fd971f        208            darkyellow
" Color: diffAdd               #5faf5f        71             darkgreen
" Color: diffDelete            #af5f5f        131            darkred
" Color: diffChange            #5f87af        67             darkblue
" Color: diffText              #af87af        139            darkmagenta
" Color: black                 #000000        16             black
" Color: white                 #dadada        253            white
" Color: Added                 #5fd75f        77             darkgreen
" Color: Changed               #ffaf5f        215            darkyellow
" Color: Removed               #d75f5f        167            darkred
" Term colors: color00 color01 color02 color03 color04 color05 color06 color07
" Term colors: color08 color09 color10 color11 color12 color13 color14 color15
" vim: et ts=8 sw=2 sts=2
