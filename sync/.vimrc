set nocompatible
filetype off
    set rtp+=~/.vim/bundle/Vundle.vim
call vundle#begin()
" Install Vundle per the github instructions
" Run the following command in vim to install the plugins
" :PluginInstall 
Plugin 'VundleVim/Vundle.vim'
Plugin 'vim-syntastic/syntastic'
Plugin 'davidhalter/jedi-vim'
Plugin 'OmniCppComplete'
Plugin 'townk/vim-autoclose'
Plugin 'itchyny/lightline.vim'
Plugin 'majutsushi/tagbar'
Plugin 'wincent/ferret'
" Plugin 'brooth/far.vim'
" Plugin 'dkprice/vim-easygrep'
Plugin 'tpope/vim-commentary'
Plugin 'airblade/vim-rooter'
"autoformat will look for system installed formatters. See docs
Plugin 'Chiel92/vim-autoformat'
" Plugin 'vim-vdebug/vdebug' 
" Plugin 'ervandew/supertab'
call vundle#end()
packadd termdebug

" set signcolumn=yes
" always 10 lines around cursor
set cursorline
hi CursorLine cterm=NONE ctermbg=black
set scrolloff=10
set autoindent
set smartindent
set tabstop=4
set shiftwidth=4
" set expandtab
" set textwidth=120
set t_Co=256
syntax on
"filetype indent plugin on
filetype plugin on
set nocp
set number
set nowrap
" set showmatch
set noshowmatch
" Disable the annoying highlight of matching parenthesis
" function! g:DisableMatchParen ()
"     if exists(":NoMatchParen")
"         :NoMatchParen
"     endif
" endfunction
" augroup plugin_initialize
"     autocmd!
"     autocmd VimEnter * call DisableMatchParen()
" augroup END
set comments=sl:/*,mb:\ *,elx:\ */
set mouse=a
set path+=**
set wildmenu
set clipboard=unnamed
set tabpagemax=15
set showtabline=2
hi Normal guibg=NONE ctermbg=NONE
hi Visual term=reverse ctermfg=0
hi DiffChange term=reverse ctermfg=0
hi SpellBad term=reverse ctermfg=0
hi SpellRare term=reverse ctermfg=0
hi CursorColumn term=reverse ctermfg=0
hi ColorColumn term=reverse ctermfg=0
hi ToolbarLine term=reverse ctermfg=0
au BufNewFile,BufRead *.cu set filetype=cuda
au BufNewFile,BufRead *.cuh set filetype=cuda
set whichwrap+=<,>,[,]
set foldmethod=syntax
set foldnestmax=5
set nofoldenable
set foldlevel=3
map <Esc>[; <C-Semicolon>
map! <Esc>[; <C-Semicolon>
set backspace=indent,eol,start
map <BS> i<BS>
map <DEL> i<DEL>
" These are bindings for copy and paste!
noremap <C-a> ggVG<CR><CR>
vnoremap <C-c> :w !xsel -i -b<CR><CR>
noremap <C-v> :r !xsel -o -b<CR><CR>
"map <C-k> <C-E>
"map <C-l> <C-Y>
map <C-s> :split<CR>
map <C-d> :vsplit<CR>
noremap <space> :
noremap ; l
noremap l k
noremap k j
noremap j h
noremap <C-k> 5j 
noremap <C-l> 5k 
noremap <C-j> 5h
noremap <C-Semicolon> 5l
set timeoutlen=300 ttimeoutlen=0
" remapping arrow keys to move splits
nnoremap <F1> :tabprevious<CR>
nnoremap <F2> :tabnext<CR>
nnoremap <C-u> :vertical resize -5<CR>
nnoremap <C-p> :vertical resize +5<CR>
nnoremap <C-o> :resize -3<CR>
nnoremap <C-i> :resize +3<CR>
" nnoremap <C-W> B
map <C-w>j :wincmd h<CR>
map <C-w>k :wincmd j<CR>
map <C-w>l :wincmd k<CR>
map <C-w>; :wincmd l<CR>
map a A
inoremap kj <Esc>
set tags=./.tags;/
set background=light

"syntastic
" set statusline+=%#warningmsg#
" set statusline+=%{SyntasticStatuslineFlag()}
" set statusline+=%*
let g:syntastic_always_populate_loc_list=1
let g:syntastic_auto_loc_list=1
let g:syntastic_check_on_open=0
let g:syntastic_check_on_wq=0
let g:syntastic_quiet_messages={"type": "style"}
let g:syntastic_enable_highlighting=1
let g:syntastic_quiet_messages = {
	\ "level": "warnings",
	\ "type":   "style",
	\ "regex":  'warning',
	\ "file:p": ['.py$'] }
" let g:syntastic_enable_balloons=1
let g:syntastic_enable_signs=0
let g:syntastic_loc_list_height=4
let b:syntastic_mode="active"
noremap <silent> <F12> :SyntasticCheck<CR>

"jedi vim
let g:jedi#documentation_command = "<leader>K"

"Find and replace
nnoremap <C-r> :%s/
nnoremap <C-f> :/

"lightline plugin
set laststatus=2
set noshowmode

"Rooter plugin
" let g:rooter_manual_only=1

"netrw vim tree
let g:netrw_liststyle=3
let g:netrw_banner=0
let g:netrw_browse_split=4
let g:netrw_winsize=15
let g:NetrwIsOpen=0

function! ToggleNetrw()
    if g:NetrwIsOpen
        let i = bufnr("$")
        while (i >= 1)
            if (getbufvar(i, "&filetype") == "netrw")
                silent exe "bwipeout " . i 
            endif
            let i-=1
        endwhile
        let g:NetrwIsOpen=0
    else
        let g:NetrwIsOpen=1
        silent Lexplore
    endif
endfunction

" Add your own mapping. For example:
noremap <silent> <C-T> :call ToggleNetrw()<CR>

"Autoformat Plugin - utilizes formatters installed on system
" the following line will call Autoformat on save
"au BufWrite * :Autoformat
map F :Autoformat<CR>
let g:autoformat_autoindent = 0
let g:autoformat_retab = 0
let g:autoformat_remove_trailing_spaces = 0

"Tagbar Plugin
nnoremap <C-b> :TagbarToggle<CR>

"Vdebug Plugin
" au BufNewFile,BufRead *.py map <F1> :!python -S /usr/bin/py3_dbgp -d localhost:9000 %:t &<CR>

" let g:vdebug_force_ascii = 1
" let g:vdebug_keymap = {
" \    'run' : '<F5> ',
" \    'run_to_cursor' : '<F4>',
" \    'step_over' : '<F10>',
" \    'step_into' : '<F11>',
" \    'step_out' : '<F12>',
" \    'close' : '<F6>',
" \    'detach' : '<F7>',
" \    'set_breakpoint' : '<F9>',
" \    'get_context' : '<Leader><F11>',
" \    'eval_under_cursor' : '<F8>',
" \    'eval_visual' : '<Leader>e'
" \}

"termdebug Plugin
let g:termdebug_wide = 1
let termdebugger = "gdb"
au BufNewFile,BufRead *.c* map <F1> :Termdebug<CR>
au BufNewFile,BufRead *.c* map <F2> :call TermDebugSendCommand('dashboard -layout expressions variables')<CR>
au BufNewFile,BufRead *.c* map <F4> :Run<CR>
au BufNewFile,BufRead *.c* map <F5> :Continue<CR>
au BufNewFile,BufRead *.c* map <F6> :call TermDebugSendCommand('quit')<CR>
au BufNewFile,BufRead *.c* map <F9> :Break<CR>
au BufNewFile,BufRead *.c* map <F10> :Over<CR>
