from pathlib import Path
import json
import re

ROOT = Path('E:/PY/TTC/presentation/presentation paper')
source = ROOT / 'test-time-compute-25min.tex'
text = source.read_text(encoding='utf-8')

# These exact sentences also appear in the Word script.
conclusions = {
    'search_overall': [
        'Beam search is strongest at low budgets, but its advantage shrinks as compute increases.',
        'At matched cost, extra lookahead usually gives less benefit.',
    ],
    'search_difficulty': [
        'Extra search can hurt easy questions, help medium difficulty questions, and still fail on the hardest ones.',
        'Both question difficulty and compute budget should guide the search setting.',
    ],
    'search_adaptive': [
        'Difficulty-based allocation improves search efficiency.',
        'At low budgets, 16 generations nearly match best-of-N with 64.',
        'Predicted difficulty loses some of its advantage at higher budgets.',
    ],
    'revision_quality': [
        'Revision improves single-answer accuracy, then the gains level off.',
        'Sequential sampling slightly beats independent sampling with either selection rule.',
    ],
    'revision_mix': [
        'At high budgets, a mixture can beat either pure parallel or pure sequential generation.',
        'Easy questions favor long chains; harder questions often benefit from more independent starts.',
        'The best mix depends on both difficulty and budget.',
    ],
    'revision_adaptive': [
        'Adaptive revisions keep improving after parallel sampling begins to plateau.',
        '64 candidates can beat parallel best-of-N with 256 candidates.',
    ],
    'model_comparison': [
        'Extra inference often wins on easy or medium questions, especially when expected inference use is low.',
        'A larger model is often better on very hard questions or when expected inference use is high.',
    ],
    'r_example': [
        'The better choice depends on both question difficulty and expected use.',
    ],
}

def frame_replace(title, replacement):
    global text
    pattern = r'\\begin\{frame\}\{' + re.escape(title) + r'\}.*?\\end\{frame\}'
    text, count = re.subn(pattern, lambda _: replacement, text, count=1, flags=re.S)
    assert count == 1, title

frame_replace('How Well Does Search Scale with More Compute?', r'''\begin{frame}{Beam Search Helps Most at Low Budgets}
  {\small PaLM 2-S* on MATH: 12,000 training questions and 500 test questions.}
  \par\medskip
  \begin{columns}[T,onlytextwidth]
    \begin{column}{.58\textwidth}
      \centering
      \paperfig[.61\textheight]{9}{61 539 309 708}{\linewidth}
    \end{column}
    \begin{column}{.39\textwidth}
      \small
      \textbf{Beam search is strongest at low budgets, but its advantage shrinks as compute increases.}
      \par\medskip
      At matched cost, extra lookahead usually gives less benefit.
      \par\medskip
      The authors attribute diminishing returns partly to exploitation of PRM scoring errors.
    \end{column}
  \end{columns}
  \note{Time 7:45--9:00. Read Figure 3 left by comparing methods vertically at the same budget. Follow the beam-search curves from the low-budget region to higher budgets and compare with weighted best-of-N. Explain that lookahead's extra rollouts are charged to the budget. State both displayed conclusions. Scorer exploitation is the authors' explanation, supported by their examples. Then ask whether the aggregate trend hides different outcomes across question difficulty.}
\end{frame}''')

frame_replace('Are Search Failures Confined to Hard Questions?', r'''\begin{frame}{Difficulty Changes Which Search Strategy Wins}
  Five difficulty groups relative to the base model, from 1 (easiest) to 5 (hardest).
  \par\medskip
  \begin{columns}[T,onlytextwidth]
    \begin{column}{.57\textwidth}
      \centering
      \paperfig[.61\textheight]{9}{315 539 551 708}{\linewidth}
    \end{column}
    \begin{column}{.40\textwidth}
      \small
      \textbf{Extra search can hurt easy questions, help medium difficulty questions, and still fail on the hardest ones.}
      \par\medskip
      Bins 1--2 can show over-optimization; beam search is stronger in bins 3--4; bin 5 barely improves.
      \par\medskip
      \keyterm{Both question difficulty and compute budget should guide the search setting.}
    \end{column}
  \end{columns}
  \note{Time 9:00--11:15. Explain the four budget positions in every bin: 4, 16, 64, and 256. The three colored bars overlap at each position and all start at zero. They are not stacked contributions. First read the easiest group at budget 4, where blue is highest, orange is next, and green is lowest. Then follow budgets within the group and compare with bins 3--4 and the hardest bin. State the two displayed conclusions. Formal bin estimation remains in backup.}
\end{frame}''')

frame_replace('Choosing Search Settings by Difficulty and Budget', r'''\begin{frame}{Difficulty-Based Allocation Improves Search Efficiency}
  \begin{columns}[T,onlytextwidth]
    \begin{column}{.58\textwidth}
      \centering
      \paperfig[.63\textheight]{10}{306 466 551 635}{\linewidth}
    \end{column}
    \begin{column}{.39\textwidth}
      \small
      \textbf{Difficulty-based allocation improves search efficiency.}
      \par\medskip
      At low budgets, 16 generations nearly match best-of-$N$ with 64.
      \par\medskip
      Predicted difficulty loses some of its advantage at higher budgets.
    \end{column}
  \end{columns}
  \par\smallskip
  {\small These generation budgets exclude difficulty-estimation cost.}
  \note{Time 11:15--12:00. Compare the adaptive blue/orange curves with PRM weighted best-of-N in green. Compare at the same accuracy across budgets to illustrate 16 versus 64. Distinguish true-correctness oracle bins from verifier-predicted bins. The result is a low-budget saving, and estimating difficulty is excluded. Then return to the second route: revising full answers.}
\end{frame}''')

frame_replace('Revision Quality and Final Answer Accuracy', r'''\begin{frame}{Revisions Improve Quality but Have Diminishing Returns}
  \begin{center}
    \paperfig[.44\textheight]{12}{61 539 551 715}{.98\textwidth}
  \end{center}
  \begin{itemize}
    \item Revision improves single-answer accuracy, then the gains level off.
    \item Sequential sampling slightly beats independent sampling with either selection rule.
  \end{itemize}
  \par\smallskip
  \keyterm{More rounds help overall, but each additional round gives less benefit.}
  \note{Time 13:15--15:00. First read the left panel: revision position on x, single-answer accuracy on y. Four trajectories per question supply each position's mean; early improvement gives way to a noisy plateau. Then read the right panel at a fixed candidate count. Compare sequential and parallel under the same selection rule. Verifier weighted selection is the upper pair and majority is the lower pair. State the two displayed empirical conclusions. Ask whether independent starts and revisions should be combined.}
\end{frame}''')

frame_replace('Combining Fresh Starts with Revisions', r'''\begin{frame}{The Best Mix Depends on Difficulty and Budget}
  \begin{center}
    \paperfig[.44\textheight]{13}{61 539 551 708}{.98\textwidth}
  \end{center}
  \small
  \begin{itemize}
    \item At high budgets, a mixture can beat either pure parallel or pure sequential generation.
    \item Easy questions favor long chains; harder questions often benefit from more independent starts.
  \end{itemize}
  \par\smallskip
  \keyterm{The best mix depends on both difficulty and budget.}
  \note{Time 15:00--16:45. The left x-axis is chain length divided by chain count. A line keeps their product, the total budget, fixed. Color is budget on the left and ratio on the right. The right panel fixes 128 generations and groups by difficulty. Read a peak within a fixed-budget curve and then compare colors within difficulty bins. State all three displayed conclusions.}
\end{frame}''')

frame_replace('Compute-Optimal Revisions Improve Scaling', r'''\begin{frame}{Adaptive Revisions Use the Generation Budget More Efficiently}
  \begin{columns}[T,onlytextwidth]
    \begin{column}{.58\textwidth}
      \centering
      \paperfig[.63\textheight]{13}{306 186 551 357}{\linewidth}
    \end{column}
    \begin{column}{.39\textwidth}
      \small
      \textbf{Adaptive revisions keep improving after parallel sampling begins to plateau.}
      \par\medskip
      \keyterm{64 candidates can beat parallel best-of-$N$ with 256 candidates.}
      \par\medskip
      Both oracle and predicted difficulty improve the allocation.
    \end{column}
  \end{columns}
  \par\smallskip
  {\small The reported saving excludes difficulty-estimation cost.}
  \note{Time 16:45--17:45. Figure 8 compares adaptive mixtures with pure parallel sampling. Solid lines use weighted best-of-N and dashed lines use majority. Colors distinguish oracle, predicted, and parallel. Compare within a selection rule. Read across budgets for the 64-versus-256 example. State the displayed conclusions and the excluded difficulty cost. Next compare extra inference with larger model size at equal total FLOPs.}
\end{frame}''')

frame_replace('Small Model with Extra Compute versus Larger Model', r'''\begin{frame}{Extra Inference Can Beat a Larger Model in Some Settings}
  \begin{center}
    \paperfig[.47\textheight]{15}{64 526 549 715}{.98\textwidth}
  \end{center}
  \small
  \begin{itemize}
    \item Extra inference often wins on easy or medium questions, especially when expected inference use is low.
    \item A larger model is often better on very hard questions or when expected inference use is high.
  \end{itemize}
  \par\smallskip
  \keyterm{The comparison depends on both difficulty and the expected inference workload.}
  \note{Time 20:30--22:45. Read Figure 9. Curves are adaptive inference with the small model, stars are greedy answers from the model with about 14 times more parameters. Match color and the workload's vertical line. A curve higher than the star favors additional inference. The same star height repeats at different matched budgets. Purple easy questions and blue hardest questions show different patterns. State both displayed conditional findings. The next slide follows one medium-difficulty group through the three R values. Figure 9 uses oracle difficulty bins.}
\end{frame}''')

case_frame = r'''\begin{frame}{Expected Use Can Change Which Model Is Better}
  One example: the \textbf{revision model on difficulty bin 3}, read from the previous figure.
  \par\medskip
  \begin{center}
  \small
  \begin{tabular}{ccl}
    \toprule
    $R$ & \shortstack{Small-model inference\\budget multiplier} & Matched-cost outcome\\
    \midrule
    $22$ & $\sim16\times$ & The larger model is more accurate.\\[2mm]
    $0.79$ & $\sim64\times$ & The two models are close.\\[2mm]
    $0.16$ & $\sim256\times$ & The small model with revisions is more accurate.\\
    \bottomrule
  \end{tabular}
  \end{center}
  \par\medskip
  Lower expected use lets the small model spend more of its training savings on each inference.
  \par\medskip
  \keyterm{The better choice depends on both question difficulty and expected use.}
  \note{Time 22:45--23:45. Follow the green revision curve for difficulty bin 3 in Figure 9. At the high-workload R of 22, the matched budget is near 16 and the larger model's star is higher. Around R=0.79 the matched budget is near 64 and the two are close. At R=0.16 the matched budget is near 256 and the revision curve is higher. These are approximate plot locations for the rounded R values. This is an example for one group and method. The broader conditional conclusions remain those on the preceding slide.}
\end{frame}

'''
text = text.replace(r'\begin{frame}{Limits of the Comparison}', case_frame + r'\begin{frame}{Limits of the Comparison}', 1)
text = text.replace('Time 23:15--24:15.', 'Time 23:45--24:30.', 1)
text = text.replace('Time 24:15--25:00.', 'Time 24:30--25:00.', 1)

main = text.split(r'\appendix', 1)[0]
times = re.findall(r'Time (\d+):(\d+)--(\d+):(\d+)', main)
last = 0
for a,b,c,d in times:
    start,end = int(a)*60+int(b),int(c)*60+int(d)
    assert start == last, (start,last)
    last = end
assert last == 1500
source.write_text(text, encoding='utf-8')
Path('E:/PY/TTC/.presentation-review/takeaways.json').write_text(json.dumps(conclusions,indent=2),encoding='utf-8')
print('Updated result slides and added the R example. Planned talk remains 25 minutes.')
