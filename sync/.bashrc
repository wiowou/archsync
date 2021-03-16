#
# ~/.bashrc
#
# If not running interactively, don't do anything
[[ $- != *i* ]] && return

#PS1='[\u@\h \W]\$ '
#change cursor to blinking bar
printf '\033[5 q]'
stty -ixon #disable freeze on C-s 
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8
export LC_CTYPE=en_US.UTF-8
export MOZ_ENABLE_WAYLAND=1
export githubhttp="https://github.com/wiowou"
export github="ssh://git@github.com/wiowou"
export gitpriv="/home/bk/mnt/nas/gitrepo"
export VISUAL=vim
export EDITOR="$VISUAL"
export PAGER=less
export karst="bkapadia@karst.uits.iu.edu"
export bigred2='bkapadia@bigred2.uits.iu.edu'
export CUDA_HOME=/opt/cuda
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:${CUDA_HOME}/lib64 #/usr/lib/nvidia
export PATH=$PATH:$CUDA_HOME/bin:$HOME/bin #:$HOME/eclipse/parallel-oxygen/eclipse
export PYTHONPATH=$HOME/lib/python
export PYTHONBREAKPOINT="pudb.set_trace"
#export CUDA_DEBUGGER_SOFTWARE_PREEMPTION=1

alias ls='ls --color=auto --group-directories-first'
alias ll='ls --color=auto --group-directories-first -alF'
alias la='ls --color=auto --group-directories-first -A'
alias tree='tree -C -L 1 -h'
alias scp-iu='scp -i /home/bk/mnt/samsung/iu/scomp'
alias memcheck='valgrind --log-file=valgr.log --leak-check=full'
alias lsblk='lsblk -f'
alias netmap='nmap -sP 192.168.1.0/24'
alias mkproj='python -m mkproj'
alias mksrc='python -m mksrc'
alias pym='python -m pym'
alias mount-usb='sudo mount -t vfat /dev/sdc1 ~/mnt/usb -o uid=bk,gid=users'
alias mount-cam='sudo mount -t exfat /dev/sdc1 ~/mnt/usb -o uid=bk,gid=users'
alias rsync-cam='rsync -a ~/mnt/usb/DCIM/100_PANA/* ~/mnt/shared/pictures/arden/cam'
alias mount-mmc='sudo mount -t vfat /dev/mmcblk0p1 ~/mnt/usb -o uid=bk,gid=users'
alias usage='ps -eo pid,ppid,cmd,%mem,%cpu, --sort=-%cpu | head -n 15'
#alias suspend='systemctl suspend'
alias pdf='masterpdfeditor4'
alias ctags='ctags -h .h.cuh.hpp.py -a --exclude=node_modules -f ./.tags .'
alias du='du -sh'
alias feh='feh -F'
alias cmus='cd /home/bk/mnt/shared/music; cmus'
alias chrome='chromium'
alias fetchsong='cd /home/bk/mnt/shared/music/YouTube; youtube-dl -x -f bestaudio -o "%(title)s.%(ext)s"'
alias fetchplaylist='cd /home/bk/mnt/shared/music/YouTube; youtube-dl -x -f bestaudio -o "%(playlist)s/%(playlist_index)s-%(title)s.%(ext)s"'
alias backup='push-all-server'
alias cd='
    function _cd() {
        dest=$HOME
        if [ $# -gt 0 ]; then
            dest=$1
        fi
        cd "$dest"
		pwd > $HOME/.cwd
        ls
    }; _cd'
alias wd='
    function _wd() {
        dest=$HOME
        if [ -f $HOME/.cwd ]; then
            dest=`cat $HOME/.cwd`
        fi
        cd $dest
    }; _wd'
alias mongosandbox='mongo "mongodb+srv://sandbox.mr5rc.mongodb.net/Sandbox" --username m001-student'
