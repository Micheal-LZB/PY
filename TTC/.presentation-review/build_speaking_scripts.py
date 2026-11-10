from pathlib import Path
import json
import re
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

ROOT = Path('E:/PY/TTC/presentation/presentation paper')
T = json.loads(Path('E:/PY/TTC/.presentation-review/takeaways.json').read_text(encoding='utf-8'))

MAIN = [
    dict(title='Title page', speech='''Today I will present a paper about using more computation when a language model answers a question. The main idea is that a model can try several solutions, revise earlier answers, or search with feedback. The paper asks how to use this extra work well, and when it can be more useful than training a larger model.'''),
    dict(title='Can Language Models Benefit from More Thinking?', speech='''When we face a difficult problem, we often spend longer thinking about it. We may check an early answer, notice an error, and change our reasoning. This can help us reach a better decision.

Can a language model do something similar? After training, can it use extra computation to give a better answer? The paper calls this test-time compute. The question is how to turn that extra computation into a real improvement in accuracy.'''),
    dict(title='How Do We Work through a Math Problem?', speech='''Think about solving a math problem with classmates. One option is to ask several people to work independently, then compare their answers. This gives us several possible approaches.

We could also read an earlier attempt and improve it. Or we could ask someone to check our unfinished reasoning before we continue.

These familiar actions suggest different uses of model computation. We can generate independent attempts, revise existing answers, or get feedback during generation. The paper studies how these choices affect the final result.'''),
    dict(title='Two Directions for Using Extra Computation', speech='''The starting point is best-of-N. The model independently generates N complete solutions, and a verifier helps select the final answer. This is like several classmates solving the same question separately.

The paper then considers two improvements. First, we can change what the model generates by giving it earlier answers and asking for revisions. This changes its proposal distribution, meaning the probabilities of the answers it generates.

Second, we can use feedback while the solution is still being written. A verifier scores partial reasoning, and search decides which paths deserve more work. We will follow this second route first.'''),
    dict(title='PRM-Guided Search from Steps to an Answer', cue='Point to a gray cross, then follow a retained branch through the next expansion.', speech='''Start from the question and follow the branches. The model proposes several first steps. The PRM scores each partial solution. A gray node with a cross stops here. We spend no more generation compute on that branch.

Each retained prefix can produce different next steps. We score these longer prefixes and prune again. The dots mean we repeat this process. Only surviving paths become complete answers for final selection.

Best-of-N completes all its independent candidates before selection. Here, feedback during generation decides which branches receive more compute. This leaves three questions. Who gives the scores? How do we choose the final answer? And which candidates should we retain? The next slides answer these in order.'''),
    dict(title='Who Can Score the Reasoning?', speech='''We train a process reward model, or PRM, to give the scores. Look first at the solid box. It contains the question and all reasoning up to the current step. We keep this prefix fixed.

From this same prefix, the base model samples four independent continuations, each all the way to a final answer. The dashed boxes and paths show these possible futures. We check the final answers against the ground truth. Three checks and one cross mean three correct answers out of four. The brace groups these results, giving 0.75 as the training target for the current prefix. Four is just an example.

We repeat this for many prefixes and train the PRM to predict these targets. During search, the trained PRM scores a new prefix directly. We do not run these four continuations again every time we need a score. The prediction estimates the chance that the base model will finish correctly from here.'''),
    dict(title='How Do We Select the Final Answer?', cue='Point to the two x equals 2 candidates, then their summed score.', speech='''Once a solution is complete, we use its last-step PRM score as the score of that whole solution. The last-step prediction sees the entire preceding solution.

Now consider these three candidates. Two give x equals 2, with scores 0.60 and 0.55. One gives x equals 3, with score 0.90. Weighted best-of-N adds scores for the same final answer. So x equals 2 receives 1.15 and wins.

Standard best-of-N would choose the single highest-scoring candidate. Majority voting counts matching answers without using these weights. Here we use weighted selection to combine support from different solutions.'''),
    dict(title='Which Candidates Should We Develop?', cue='Move through the three diagrams from independent generation to stepwise search.', takeaways=['Lookahead spends additional compute on its temporary continuations.'], speech='''The third question is how to generate and keep the candidates. The three diagrams show three choices.

Best-of-N independently generates complete solutions and selects afterward. Beam search brings the verifier into the generation process. At each depth, it scores the current prefixes, keeps the highest-scoring ones, and expands them again.

Lookahead changes how a prefix is evaluated. It temporarily continues for up to k more steps, then uses the PRM score at that endpoint to evaluate the current prefix. The temporary continuation helps choose where to search next.

This also costs extra computation. The comparison charges those additional steps to the budget. If k is zero, lookahead reduces to ordinary beam search. We now have a trained scorer, a search procedure, and a final selection rule. We can compare how well they work.'''),
    dict(title='Beam Search Helps Most at Low Budgets', cue='Compare vertically at one budget, then follow the beam curves as the budget rises.', takeaways=T['search_overall'], speech='''The experiments use PaLM 2-S star on the MATH benchmark, with 12,000 training questions and 500 test questions. This graph compares search methods.

The horizontal axis is the generation budget. The vertical axis is accuracy. To compare methods fairly, first look at the same horizontal position. At small budgets, beam search is stronger than weighted best-of-N. As the budget grows, this advantage shrinks, and best-of-N can catch up or pass it.

Lookahead usually gives less benefit at the same estimated cost. It spends some of its budget on temporary continuations.

The authors also suggest that stronger search can exploit mistakes in the PRM's scores. So more search does not always improve the actual answer. The overall curve now raises another question: which questions are improving, and which are getting worse?'''),
    dict(title='Difficulty Changes Which Search Strategy Wins', cue='Explain the overlapping bars before drawing any comparison.', takeaways=T['search_difficulty'], speech='''The authors divide questions into five difficulty groups relative to the base model. Group one is easiest and group five is hardest.

This graph needs a careful reading. Each group contains four positions, for budgets of 4, 16, 64, and 256. At each position, three colored bars overlap. Every bar starts at zero. We read the top of each color, rather than add the visible colored pieces.

Blue is beam search, orange is weighted best-of-N, and green is majority voting. For example, in the easiest group at budget four, beam search is highest. As the budget grows, the independent methods catch up. The paper finds signs of over-optimization by beam search in the easy groups.

In groups three and four, beam search is consistently stronger than best-of-N. In group five, all the methods make little progress.

So failures are not limited to the hardest questions. Extra search can hurt easy questions, help medium difficulty questions, and still fail on the hardest ones. This gives us a reason to choose settings using both difficulty and budget. The details of how the groups are formed are in backup.'''),
    dict(title='Difficulty-Based Allocation Improves Search Efficiency', cue='Compare the adaptive curves with the green PRM best of N curve.', takeaways=T['search_adaptive'], speech='''We can now choose the best tested search setting separately for each difficulty group and budget.

The adaptive curves improve on the fixed baseline. At low budgets, sixteen generations nearly match PRM best-of-N with sixty-four. This is the reported saving of up to about four times in generation budget.

The predicted-difficulty method loses some of its advantage at higher budgets. Also, these budgets exclude the cost of estimating difficulty. The finding is that allocation matters. Next we return to the other direction: improving what the model proposes by letting it revise full answers.'''),
    dict(title='Revising Answers and Selecting the Output', cue='Point to the red context window, then to the complete candidate sets below.', speech='''The authors fine-tune a revision model to use earlier full solutions when writing a new answer. The first call sees only the question. The second sees the question and the first answer.

At later rounds, the model sees at most the four most recent answers. In the upper diagram, answers sixty through sixty-three are the input history for generating answer sixty-four. Older answers leave the input window, but we still save them.

The lower diagram shows why saving matters. We use all the candidates for final selection. With several chains, the verifier first selects within a chain and then across chains. Two chains of length sixty-four contain 128 candidates in total.

We select from the history because the latest revision can undo a correct answer. The data construction and the measured error rate are in backup.'''),
    dict(title='Revisions Improve Quality but Have Diminishing Returns', cue='Read the fixed-position accuracy first, then compare generation styles under the same selector.', takeaways=T['revision_quality']+['More rounds help overall, but each additional round gives less benefit.'], speech='''This figure checks whether revision actually improves performance. In the first panel, the horizontal axis is the revision position. The vertical axis is the accuracy of the answer at that position. For each question, the authors run four chains of length sixty-four and average the results at each position.

Accuracy improves early, then fluctuates around a plateau. It does not rise at every individual step. Revision improves single-answer accuracy, then the gains level off.

The second panel asks a different question. After generating N candidates, how accurate is the selected final answer? Compare sequential and parallel generation using the same selection rule. The upper pair uses weighted verifier selection, and the lower pair uses majority voting.

Sequential generation is slightly better under both rules. This suggests that earlier answers can help the next attempt. But the early gains and later plateau also show diminishing returns. We should now ask whether several independent starting points could make better use of a large budget.'''),
    dict(title='The Best Mix Depends on Difficulty and Budget', cue='Follow one fixed-budget curve, then compare ratios within a difficulty group.', takeaways=T['revision_mix'], speech='''We can split the budget between independent chains and revisions inside each chain. With sixteen candidates, we could use sixteen one-answer chains, four chains of length four, or one chain of length sixteen.

In the first panel, every line keeps the total budget fixed. The horizontal axis is chain length divided by chain count. Moving right means longer chains and fewer independent starts. At high budgets, the peak can be between the two extremes. A mixture can beat either pure parallel or pure sequential generation.

The second panel fixes the budget at 128 and compares question difficulty. Here the color represents the sequential-to-parallel ratio. Easy questions favor long chains. Harder questions often benefit from more independent starts.

The colors have different meanings in the two panels, so we compare within each panel carefully. The conclusion is that the best mix depends on both difficulty and budget. We can use this pattern to choose a ratio for each difficulty group.'''),
    dict(title='Adaptive Revisions Use the Generation Budget More Efficiently', cue='Compare matching line styles, then read across budgets for the saving.', takeaways=T['revision_adaptive'], speech='''This graph applies that adaptive choice. Colors distinguish oracle difficulty, predicted difficulty, and pure parallel generation. Solid lines use weighted best-of-N, while dashed lines use majority voting.

Compare methods with the same line style. At larger budgets, pure parallel sampling begins to plateau, while the adaptive mixtures continue improving. In the reported comparison, sixty-four candidates can beat parallel best-of-N with 256 candidates.

Both difficulty definitions help, although estimating difficulty has an extra cost excluded from the plotted budget. We have now seen gains from search and from revisions. Can these gains make a small model competitive with a larger one?'''),
    dict(title='Pretraining and Inference at Equal Total FLOPs', speech='''To answer that, we must compare total computation. Training a larger model costs more, and using it to generate answers also costs more.

Let P be the small model's parameter count. Its pretraining cost is approximately six times P times the number of training tokens. Its inference cost is approximately two times P times the total inference tokens. We call these costs X and Y.

The paper holds the training token count fixed. If parameters grow by a factor M, both costs grow by M. The total is M times the sum of X and Y.

The small model still spends X on training. We choose its inference multiplier a so that X plus aY equals the larger model's total cost. This equation sets an equal budget. We then compare accuracy. It includes the fact that each token is more expensive for the larger model.'''),
    dict(title='Inference Workload Determines the Exchange Rate', speech='''The amount of extra inference the small model can afford depends on expected use. R is the total number of inference tokens divided by pretraining tokens. It describes the overall workload, rather than just the length of one answer.

Solving the equal-cost equation gives the multiplier a shown here. When R is small, the training savings can be spread over relatively few inference tokens. That allows much more extra computation for each problem. When R is large, the same savings must support much more use.

For a model about fourteen times larger, the three R values correspond roughly to inference multipliers near 256, 64, and 16. The table uses rounded estimates. These three settings determine the matched comparison points in the next figure.'''),
    dict(title='Extra Inference Can Beat a Larger Model in Some Settings', cue='Match a color and a vertical line before comparing a star with a curve.', takeaways=T['model_comparison'], speech='''The curves show the small model with adaptive extra inference. The first panel uses revisions and the second uses PRM search. Colors represent difficulty. The stars show greedy accuracy from a model with about fourteen times more parameters.

The horizontal axis is proportional to inference compute. Each vertical line is a matched-total-cost point for one R value. We compare the same color at that line. If the curve is above the star, extra inference on the small model is more accurate. If the star is above the curve, the larger model is more accurate.

The same large-model star appears at several horizontal positions with the same height. Its accuracy has stayed the same. The horizontal position changes because expected use changes the small model's affordable inference budget.

Easy and medium questions often favor extra inference, especially with lower expected use. Very hard questions often favor the larger model. Higher expected use also leaves less extra inference for the small model.

These are conditional findings. The comparison uses oracle difficulty groups and fixed pretraining token counts. Let us follow one medium-difficulty group to see exactly how the three R values can change the result.'''),
    dict(title='Expected Use Can Change Which Model Is Better', cue='Follow the table from high expected use to low expected use.', takeaways=T['r_example'], speech='''This table follows the green revision curve for difficulty group three. At R equal to twenty-two, expected use is high. The small model's matched inference multiplier is near sixteen, and the larger model is more accurate.

At R around zero point seven nine, the matched multiplier is near sixty-four. The models are close. At R equal to zero point one six, expected use is lower. The small model can use a multiplier near 256 and becomes more accurate with revisions.

The models and question group are the same. Their affordable inference budgets change with the workload. This example shows why the better choice depends on both question difficulty and expected use.'''),
    dict(title='Limits of the Comparison', speech='''There are limits to these results. First, estimating difficulty itself uses computation, which is excluded from the reported budgets. Second, the hardest questions gain little from the tested methods.

The experiments also use one base model on MATH, with fine-tuning for verification and revision. Other models and tasks may behave differently. Finally, the larger-model comparison keeps training data fixed and uses oracle difficulty groups. These conditions matter when applying the result to a real workload.'''),
    dict(title='Conclusions', speech='''The main finding is that how we spend inference compute matters. The best setting depends on both the question and the budget.

Adaptive search and revisions can give large generation-budget savings in these experiments. Extra inference can also outperform a larger model in some settings. The hardest questions and high expected use can favor more pretraining. That is the condition behind the paper's title.'''),
    dict(title='Questions', speech='''Thank you for listening. I am happy to take questions.'''),
]

BACKUP = [
    dict(title='Backup: Constructing Revision Training Data', speech='''The revision model needs examples of how earlier answers can lead to a corrected answer. The authors independently sample sixty-four full solutions to a training question at a higher temperature.

For each correct target, they select zero to four incorrect answers from the same set as context. The number is sampled uniformly from those five options. Character edit distance helps prioritize incorrect answers related to the correct one.

The small equation example shows the purpose. Both solutions reach two x equals four. The incorrect reference then says x equals four. The target keeps the valid setup and changes the last calculation to x equals two. The model learns to use earlier work when producing a new solution.

These are training pairs assembled after independent sampling. During inference, the context window simply keeps the most recent four answers in order. Edit distance is used to build the training examples.'''),
    dict(title='Backup: Why the Last Revision Can Be Wrong', cue='Point to the correct middle answer, then the incorrect final revision.', speech='''Training contexts contain incorrect reference answers followed by a correct target. During inference, the earlier answers are generated by the revision model itself, so they can already be correct.

This difference creates a distribution shift. A model may keep revising a solution that was already right. The diagram illustrates a wrong answer becoming correct and then becoming wrong again. It is a schematic example.

Under the authors' naive revision approach, about thirty-eight percent of correct answers were converted to incorrect answers. The denominator is correct answers, rather than every generated answer.

This explains the use of final selection from the history. A verifier or majority voting gives the system a chance to recover a correct answer produced earlier. Selection itself can still make mistakes.'''),
    dict(title='Backup: A Complete Beam-Search Example', cue='Walk through one round with six candidates, then repeat the same rule.', speech='''Here is the numerical beam-search procedure used in our earlier overview. Let N be six and M be two. First sample six possible first steps. Score the entire prefix of each with the trained PRM.

Keep the highest-scoring N divided by M prefixes, which is three. From each retained prefix, sample two next steps. We now have six longer candidates again.

Score all six together and repeat. Two descendants of the same prefix can both survive. The method is selecting across the whole pool of candidates. It continues until solutions finish or the maximum of forty expansion rounds is reached.

The final candidates are evaluated using weighted best-of-N. Their matching final answers receive summed scores, and one final answer is returned. N is the size of the candidate pool, while M controls how many continuations each retained prefix receives in this implementation.'''),
    dict(title='Backup: Difficulty Estimation and Policy Selection', speech='''Difficulty is defined relative to the base model. For each test question, the authors independently sample 2,048 full answers.

Oracle difficulty uses ground-truth checking to estimate the probability that one sampled answer is correct. The questions are ranked by this rate and split into five quantiles, with about one fifth in each group.

Predicted difficulty uses the same sample set but replaces correctness labels with learned verifier scores. The mean final-answer score supplies the ranking. The procedure therefore creates a separate set of five groups. A question can fall in different groups under the two definitions.

For each group and budget, the authors choose the best tested setting and evaluate it using held-out folds. This approximates an ideal per-question policy. The 2,048 samples estimate difficulty and their cost is excluded from the plotted search or revision budgets. This matters for practical efficiency.'''),
    dict(title='Backup: Difficulty Bins and Cross-Validation', speech='''After the questions have been assigned to difficulty groups, the paper uses two-fold cross-validation inside each group.

Imagine one group contains twenty questions. Split them into two sets of ten, A and B. Compare the candidate strategies on A and select the best setting for the budget. Then measure that selected strategy on B.

Next reverse the roles. Choose the setting using B and measure its performance on A. Finally average the two held-out results. The selected setting can differ between the two directions.

The point is to evaluate a strategy on questions different from the ones used to select it. The bin definitions remain based on model-relative difficulty. Oracle and predicted difficulty run this procedure with their respective groupings.'''),
    dict(title='Backup: Training Rollouts and Lookahead', speech='''The word rollout appears at two different stages. For PRM training, we sample several continuations from a solution prefix to the final answer. Their correctness rate creates a target for learning the value of that prefix.

For lookahead search, the PRM is already trained. At inference time, we temporarily continue a current candidate for up to k extra steps, using temperature zero. We ask the PRM to score the endpoint, then use that value to rank the original current prefix.

The temporary continuation helps decide which prefixes to retain. When k is zero, this becomes ordinary beam search. Larger k uses more computation, so the paper estimates the cost as N multiplied by the quantity k plus one.

The important distinction is the role of the continuation. Training rollouts create supervision. Lookahead uses a trained scorer to choose where to search.'''),
    dict(title='Backup: Deriving the Inference Multiplier', speech='''Let X and Y be the small model's baseline training and inference FLOPs. Scaling its parameters by M, while keeping token counts fixed, gives a larger-model total cost of M times the sum of X and Y.

The small model's cost with extra inference is X plus aY. Set these totals equal and solve for a. We obtain M plus the product of M minus one and X divided by Y. Using training cost six P D and inference cost two P D gives X divided by Y equal to three divided by R. Substituting this ratio gives the boxed formula. Start with M, then add three times the quantity M minus one divided by R.

The factor two comes mainly from a multiplication and an addition for each weight in the main matrix operations. Training adds backward computation. It computes gradients for weights and for the inputs that pass gradients to earlier layers, giving roughly two more forward-sized matrix calculations. The total is about six P per training token.

P already counts parameters across all layers, so the layer count is included. These are approximate FLOPs estimates. They do not measure wall-clock latency or account exactly for every attention and implementation cost.'''),
]

def frame_metadata():
    source = (ROOT / 'test-time-compute-25min.tex').read_text(encoding='utf-8')
    output = []
    for i, match in enumerate(re.finditer(r'\\begin\{frame\}(?:\[[^\]]*\])?(?:\{([^\n]*)\})?(.*?)\\end\{frame\}', source, re.S), 1):
        title = match.group(1) or 'Title page'
        timing = re.search(r'Time (\d+:\d+)--(\d+:\d+)', match.group(2))
        output.append(dict(number=i, title=title, timing=timing.groups() if timing else None))
    return output

def set_font(style, size, bold=False):
    style.font.name = 'Arial'
    style.font.size = Pt(size)
    style.font.bold = bold
    style.font.color.rgb = RGBColor(0, 0, 0)
    rpr = style.element.get_or_add_rPr()
    fonts = rpr.find(qn('w:rFonts'))
    if fonts is None:
        fonts = OxmlElement('w:rFonts')
        rpr.insert(0, fonts)
    fonts.set(qn('w:ascii'), 'Arial')
    fonts.set(qn('w:hAnsi'), 'Arial')

def clean_heading(title):
    title = title.replace('Backup: ', '')
    title = title.replace('best-of-N', 'best of N').replace('Best-of-N', 'Best of N')
    return re.sub(r'[^A-Za-z0-9 ]+', ' ', title).strip()

def create_doc(title, subtitle, sections, metadata, output_name):
    doc = Document()
    for border in doc.styles.element.xpath('.//w:pBdr'):
        border.getparent().remove(border)
    section = doc.sections[0]
    section.page_width, section.page_height = Inches(8.27), Inches(11.69)
    section.top_margin, section.bottom_margin = Inches(.72), Inches(.68)
    section.left_margin, section.right_margin = Inches(.78), Inches(.78)
    set_font(doc.styles['Normal'], 11.5)
    normal = doc.styles['Normal'].paragraph_format
    normal.line_spacing = 1.14
    normal.space_after = Pt(7)
    normal.widow_control = True
    set_font(doc.styles['Title'], 21, True)
    doc.styles['Title'].paragraph_format.space_after = Pt(6)
    set_font(doc.styles['Subtitle'], 11.5)
    doc.styles['Subtitle'].paragraph_format.space_after = Pt(15)
    set_font(doc.styles['Heading 1'], 14, True)
    hp = doc.styles['Heading 1'].paragraph_format
    hp.space_before, hp.space_after = Pt(15), Pt(5)
    hp.keep_with_next = True

    doc.add_paragraph(title, 'Title')
    doc.add_paragraph(subtitle, 'Subtitle')
    spoken_words = 0
    for record, meta in zip(sections, metadata):
        assert record['title'] == meta['title'], (record['title'], meta['title'])
        heading = f"Slide {meta['number']} {clean_heading(meta['title'])}"
        doc.add_paragraph(heading, 'Heading 1')
        if meta['timing']:
            p = doc.add_paragraph(f"{meta['timing'][0]} to {meta['timing'][1]}")
            p.paragraph_format.space_after = Pt(5)
            p.paragraph_format.keep_with_next = True
            for r in p.runs:
                r.font.size = Pt(10)
        if record.get('cue'):
            p = doc.add_paragraph('[' + record['cue'] + ']')
            p.paragraph_format.keep_with_next = True
            for run in p.runs:
                run.italic = True
                run.font.size = Pt(10.5)
        for para in record['speech'].split('\n\n'):
            doc.add_paragraph(para.strip())
        spoken_words += len(re.findall(r"\b[\w'-]+\b", record['speech']))
        if record.get('takeaways'):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(3)
            p.paragraph_format.keep_with_next = True
            p.add_run('Conclusions shown on the slide').bold = True
            for i, line in enumerate(record['takeaways']):
                p = doc.add_paragraph(line)
                p.paragraph_format.left_indent = Inches(.14)
                p.paragraph_format.space_after = Pt(4)
                p.paragraph_format.keep_with_next = i < len(record['takeaways']) - 1
                for run in p.runs:
                    run.font.size = Pt(10.5)

    footer = section.footer.paragraphs[0]
    footer.alignment = 2
    run = footer.add_run()
    field = OxmlElement('w:fldSimple')
    field.set(qn('w:instr'), 'PAGE')
    run._r.addnext(field)
    doc.core_properties.author = 'Zhenbang Lyu'
    doc.core_properties.title = title
    doc.core_properties.subject = 'Speaking script for the test time compute paper presentation'
    doc.save(ROOT / output_name)
    return spoken_words

if __name__ == '__main__':
    meta = frame_metadata()
    assert len(MAIN) + len(BACKUP) == len(meta)
    main_words = create_doc(
        'Test Time Compute Main Presentation Script',
        '25 minute talk excluding questions', MAIN, meta[:len(MAIN)],
        'test-time-compute-main-script.docx',
    )
    backup_words = create_doc(
        'Test Time Compute Backup Speaking Script',
        'Additional explanations for questions and discussion', BACKUP, meta[len(MAIN):],
        'test-time-compute-backup-script.docx',
    )
    print('Main spoken words:', main_words)
    print('Backup spoken words:', backup_words)
    print('Main and backup slide numbers verified against the saved TeX source.')
