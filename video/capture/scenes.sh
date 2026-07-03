#!/usr/bin/env bash
# ABOUTME: Renders styled "terminal + Claude Code + ReGrade MCP" scenes for the demo video.
# ABOUTME: Each function prints one beat; VHS records it into a clip. All numbers are real.
set -uo pipefail

DIM=$'\e[38;5;244m'; BOLD=$'\e[1m'; RST=$'\e[0m'
CYAN=$'\e[38;5;117m'; GRN=$'\e[38;5;114m'; YEL=$'\e[38;5;222m'; RED=$'\e[38;5;210m'
MAG=$'\e[38;5;183m'; ORANGE=$'\e[38;5;215m'; BLUE=$'\e[38;5;111m'

# "type" a command at a shell prompt, char by char
cmd() {
  printf '%s ' "${GRN}\$${RST}"
  local s="$1" i
  for ((i=0; i<${#s}; i++)); do printf '%s' "${s:$i:1}"; sleep 0.018; done
  printf '\n'; sleep 0.5
}
out()    { printf '%s\n' "$1"; sleep "${2:-0.35}"; }
user()   { printf '%s\n' "${DIM}› ${1}${RST}"; sleep 0.8; }
claude() { printf '%s %s\n' "${MAG}●${RST}" "$1"; sleep "${2:-0.7}"; }
tool()   { printf '%s %s\n' "${GRN}⏺${RST}" "${DIM}${1}${RST}"; sleep 0.6; }
hr()     { printf '%s\n' "${DIM}────────────────────────────────────────────────────${RST}"; }

# ask(): the customer types a plain-English message into the Claude Code prompt box.
ask() {
  local text="$1" W=66 i shown pad
  local CUR="${CYAN}▊${RST}"
  printf '\e[?25l'
  printf '  %s╭%s╮%s\n' "$DIM" "$(printf '─%.0s' $(seq 1 $W))" "$RST"
  for ((i=1; i<=${#text}; i++)); do
    shown="${text:0:i}"
    pad=$(( W - 4 - ${#shown} )); (( pad < 0 )) && pad=0
    printf '\r  %s│%s %s❯%s %s%s%*s%s│%s' \
      "$DIM" "$RST" "$CYAN" "$RST" "$shown" "$CUR" "$pad" "" "$DIM" "$RST"
    sleep 0.034
  done
  printf '\n'
  printf '  %s╰%s╯%s\n' "$DIM" "$(printf '─%.0s' $(seq 1 $W))" "$RST"
  printf '\e[?25h'
  sleep 0.9
}

title() {
  echo; echo; echo
  out "   ${CYAN}${BOLD}hello-ReGrade-perf${RST}" 0.7
  out "   ${DIM}catch performance regressions in your API — under real load${RST}" 1.0
  echo
  out "   ${DIM}record  ${BLUE}→${DIM}  stress-replay  ${BLUE}→${DIM}  analyze  ${BLUE}→${DIM}  the slowdown appears${RST}" 2.4
}

beat_problem() {
  out "${DIM}# a functional test only checks WHAT your API returns${RST}" 1.0
  echo
  out "  ${GRN}✓${RST} status 200      ${GRN}✓${RST} same JSON      ${GRN}✓${RST} tests pass" 1.6
  echo
  out "${DIM}  …but it never sees:${RST}" 0.9
  out "  ${RED}✗${RST} a response that got ${BOLD}2× slower${RST}" 1.2
  out "  ${RED}✗${RST} an endpoint that ${BOLD}collapses under load${RST}" 1.8
  echo
  out "  ${CYAN}ReGrade replays your real traffic — under load — and measures it.${RST}" 2.6
}

beat_setup() {
  out "${DIM}# two versions of a tiny orders API — identical responses, different speed${RST}" 0.8
  cmd "git clone https://github.com/Curtail-Inc/hello-ReGrade-perf && cd hello-ReGrade-perf"
  cmd "docker compose up -d --build"
  out "${GRN} ✓${RST} Container ${BOLD}v1${RST}  Started   ${DIM}:8001  (record)${RST}" 0.5
  out "${GRN} ✓${RST} Container ${BOLD}v2${RST}  Started   ${DIM}:8002  (stress-replay)${RST}" 1.0
  out "${DIM}  every response byte-identical between v1 and v2 — the only difference is latency${RST}" 2.4
}

beat_record() {
  out "${DIM}# terminal 1: proxy in front of v1${RST}" 0.8
  cmd "regrade proxy --target http://localhost:8001 --port 19870"
  out "${DIM}  proxying :19870 → :8001 … recording${RST}" 1.2
  echo
  out "${DIM}# terminal 2: a small, sequential baseline (the load comes later)${RST}" 0.9
  cmd "TARGET=http://localhost:19870 ./traffic/generate.sh"
  out "${BLUE} →${RST} GET /products   ×15" 0.4
  out "${BLUE} →${RST} GET /orders/{1001,1002,1003}   ×5" 0.6
  out "${GRN} ✓${RST} traffic complete   ${DIM}(one request at a time)${RST}" 1.2
  out "${GRN} ✓${RST} Recording ID: ${BOLD}dd8b269f…${RST}   31 entries" 2.2
}

beat_knobs() {
  out "${DIM}# three knobs turn a recording into a load test${RST}" 1.2
  echo
  out "  ${CYAN}--repeat${RST} ${BOLD}500${RST}        ${DIM}run the recording 500× → statistical confidence${RST}" 2.0
  out "  ${CYAN}--parallel${RST} ${BOLD}50${RST}        ${DIM}50 concurrent sessions → the real load${RST}" 2.2
  out "  ${CYAN}--pacing${RST} ${BOLD}full_speed${RST}   ${DIM}maximum pressure (or preserve_timing)${RST}" 2.6
}

beat_stress() {
  out "${DIM}# stress-replay the baseline against v2${RST}" 0.8
  cmd "regrade replay --rec-id dd8b269f --target :8002 --repeat 500 --parallel 50 --pacing full_speed"
  out "${DIM}  50 sessions · 5000 requests …${RST}" 1.2
  out "  Requests:      ${BOLD}5000${RST}" 0.5
  out "  Total deltas:  ${BOLD}${GRN}0${RST}   ${DIM}(every response byte-identical)${RST}" 1.6
  out "${DIM}  behaviorally clean — a functional test passes here. Now ask about performance.${RST}" 2.4
}

beat_analyze() {
  out "${DIM}# in Claude Code — or any MCP client${RST}" 0.7
  ask "Any performance regressions in my latest replay?"
  echo
  claude "First the behavior. ${DIM}(ReGrade MCP)${RST}"
  tool "summarize_deltas(replay_id: ecc658ec…)"
  out "  ${BOLD}0 differences${RST}   ${DIM}— nothing about the responses changed${RST}" 1.6
  echo
  claude "Now the timing:"
  tool "analyze_replay_performance(replay_id: ecc658ec…)"
  out "  ${ORANGE}GET /products${RST}     p99  ${GRN}1.9ms${RST} ${DIM}→${RST} ${RED}49ms${RST}     ${RED}+91%${RST}" 1.4
  out "  ${ORANGE}GET /orders/{id}${RST}  p99  ${GRN}11ms${RST} ${DIM}→${RST} ${RED}508ms${RST}    ${RED}+1091%${RST}" 1.8
  claude "${BOLD}Both slower. Orders is a 10× regression — behind identical responses.${RST}" 2.4
}

beat_reveal() {
  ask "Why is /orders only slow sometimes?"
  echo
  claude "It only breaks under load. Same recording, two replays:"
  echo
  out "  ${CYAN}--parallel 1${RST}     /orders p99   ${GRN}11ms → 13ms${RST}    ${DIM}(+2ms — looks fine)${RST}" 2.0
  out "  ${CYAN}--parallel 50${RST}    /orders p99   ${GRN}11ms${RST} ${DIM}→${RST} ${RED}508ms${RST}    ${RED}(+497ms — collapses)${RST}" 2.4
  echo
  claude "v2 added a lock that serializes every request. Single-shot: invisible." 2.4
  claude "${BOLD}Under concurrency: catastrophic. Only the load knob finds it.${RST}" 2.6
}

outro() {
  echo; echo
  out "   ${GRN}${BOLD}✓ a performance regression, caught under load${RST}" 0.9
  echo
  out "   ${CYAN}Try it:${RST}   ${BOLD}github.com/Curtail-Inc/hello-ReGrade-perf${RST}" 0.9
  echo
  out "   ${DIM}record → stress-replay → analyze — with ReGrade${RST}" 2.2
}

printf '\033[2J\033[3J\033[H'   # clear screen + scrollback so the clip starts fresh
"$@"
