/**
 * Google Apps Script per la creazione automatica del Google Form di Human Review (Gemma 4 (E4B))
 * Istruzioni:
 * 1. Vai su https://script.google.com/ e crea un 'Nuovo progetto'.
 * 2. Incolla questo codice nel file 'Codice.gs' sostituendo tutto.
 * 3. Clicca su 'Esegui' (Run). Autorizza l'accesso quando richiesto.
 * 4. Controlla il log di esecuzione per ottenere il link al Form generato!
 */

function createHumanReviewForm() {
  var formTitle = "📋 Human Review: Unanswerability Diagnostic Agent (Gemma 4 (E4B))";
  var form = FormApp.create(formTitle);
  form.setDescription(
    "Valutazione peritale delle risposte, cause diagnosticate e spiegazioni generate dall'Agente di VQA sul benchmark DUDE.\n\n" +
    "Per ciascuna delle 50 domande (stratificate in 5 macro-categorie), valuta la correttezza e la completezza della spiegazione fornita dall'agente.");
  form.setIsQuiz(false);
  form.setProgressBar(true);
  form.setRequireLogin(false);

  // Dati Revisore
  var nameItem = form.addTextItem();
  nameItem.setTitle("Nome / ID del Revisore");
  nameItem.setRequired(true);

  // ================= ITEM #1 =================
  var pageBreak = form.addPageBreakItem();
  pageBreak.setTitle("Item #1 — [Numerical Corruption] (measure_unit - C1)");
  pageBreak.setHelpText("❓ DOMANDA CORROTTA: \"What is 60 lbs. centi converted to 4 N.m in the metric conversion chart?\"\n📌 DOMANDA ORIGINALE: \"What is 60 lbs. ft. converted to 4 N.m in the metric conversion chart?\"\n\n⚖️ DECISIONE AGENTE: UNANSWERABLE | CAUSA PRIMARIA: DOCUMENT_ELEMENT_MISMATCH\n💬 RISPOSTA FINALE: \"Unable to determine\"\n\n📝 SPIEGAZIONE DELLA CAUSA:\n\"The question requires a conversion from 'lbs. centi' to 'N.m'. While the document contains metric conversion charts (Page 2 and Page 3), neither chart covers the specific unit 'lbs. centi', making the required conversion element mismatched with the available data.\"\n\n🔍 EVIDENZE ESTRATTE DAL DOCUMENTO: [p.2 Q3] METRIC CONVERSION: lb. ft. to N.m | [p.3 Q3] METRIC CONVERSION: kg-cm to N.m\n⚙️ PROMPT USATI: question_analysis_v1, layout_v4, layout_v4");

  var q1_1 = form.addMultipleChoiceItem();
  q1_1.setTitle("#1.1 - La spiegazione circa la causa di unanswerability è corretta?");
  q1_1.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q1_1.setRequired(true);

  var q2_1 = form.addMultipleChoiceItem();
  q2_1.setTitle("#1.2 - La spiegazione circa la causa di unanswerability è completa?");
  q2_1.setChoiceValues(["Sì", "No"]);
  q2_1.showOtherOption(true); // Permette di specificare cosa manca
  q2_1.setRequired(true);

  var q3_1 = form.addMultipleChoiceItem();
  q3_1.setTitle("#1.3 - La spiegazione contiene riferimenti corretti alle parti di documento coinvolte?");
  q3_1.setChoiceValues(["Sì", "No", "Parzialmente", "Non applicabile (nessun riferimento necessario)"]);
  q3_1.setRequired(true);

  var q4_1 = form.addMultipleChoiceItem();
  q4_1.setTitle("#1.4 - La spiegazione contiene tutti i riferimenti completi alle parti di documento coinvolte?");
  q4_1.setChoiceValues(["Sì", "No", "Non applicabile"]);
  q4_1.showOtherOption(true); // Permette di specificare cosa manca
  q4_1.setRequired(true);

  var q5_1 = form.addMultipleChoiceItem();
  q5_1.setTitle("#1.5 - La spiegazione contiene riferimenti corretti alle parti di domanda che sono causa di unanswerability?");
  q5_1.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q5_1.setRequired(true);

  var q6_1 = form.addMultipleChoiceItem();
  q6_1.setTitle("#1.6 - La spiegazione contiene tutti i riferimenti completi alle parti di domanda che sono causa di unanswerability?");
  q6_1.setChoiceValues(["Sì", "No"]);
  q6_1.showOtherOption(true); // Permette di specificare cosa manca
  q6_1.setRequired(true);

  // ================= ITEM #2 =================
  var pageBreak = form.addPageBreakItem();
  pageBreak.setTitle("Item #2 — [Numerical Corruption] (numerical_value_number - C2)");
  pageBreak.setHelpText("❓ DOMANDA CORROTTA: \"What is the number 100 that appears in the address of the image?\"\n📌 DOMANDA ORIGINALE: \"What is the number that appears in the lower right corner of the image?\"\n\n⚖️ DECISIONE AGENTE: UNANSWERABLE | CAUSA PRIMARIA: SPATIAL_MISMATCH\n💬 RISPOSTA FINALE: \"Unable to determine\"\n\n📝 SPIEGAZIONE DELLA CAUSA:\n\"The question requires finding the number 100 in the 'address of the image.' The document does not contain a distinct image with an associated address; the number 100 is visible only as a quantity in the item description, confirming a spatial mismatch.\"\n\n🔍 EVIDENZE ESTRATTE DAL DOCUMENTO: [p.1 Q3] 100 PIECES 1/2\" SHEET ASBESTOS MILL BOARD STYLE #102 4\" X 4\" AS PER\n⚙️ PROMPT USATI: question_analysis_v1, layout_v4");

  var q1_2 = form.addMultipleChoiceItem();
  q1_2.setTitle("#2.1 - La spiegazione circa la causa di unanswerability è corretta?");
  q1_2.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q1_2.setRequired(true);

  var q2_2 = form.addMultipleChoiceItem();
  q2_2.setTitle("#2.2 - La spiegazione circa la causa di unanswerability è completa?");
  q2_2.setChoiceValues(["Sì", "No"]);
  q2_2.showOtherOption(true); // Permette di specificare cosa manca
  q2_2.setRequired(true);

  var q3_2 = form.addMultipleChoiceItem();
  q3_2.setTitle("#2.3 - La spiegazione contiene riferimenti corretti alle parti di documento coinvolte?");
  q3_2.setChoiceValues(["Sì", "No", "Parzialmente", "Non applicabile (nessun riferimento necessario)"]);
  q3_2.setRequired(true);

  var q4_2 = form.addMultipleChoiceItem();
  q4_2.setTitle("#2.4 - La spiegazione contiene tutti i riferimenti completi alle parti di documento coinvolte?");
  q4_2.setChoiceValues(["Sì", "No", "Non applicabile"]);
  q4_2.showOtherOption(true); // Permette di specificare cosa manca
  q4_2.setRequired(true);

  var q5_2 = form.addMultipleChoiceItem();
  q5_2.setTitle("#2.5 - La spiegazione contiene riferimenti corretti alle parti di domanda che sono causa di unanswerability?");
  q5_2.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q5_2.setRequired(true);

  var q6_2 = form.addMultipleChoiceItem();
  q6_2.setTitle("#2.6 - La spiegazione contiene tutti i riferimenti completi alle parti di domanda che sono causa di unanswerability?");
  q6_2.setChoiceValues(["Sì", "No"]);
  q6_2.showOtherOption(true); // Permette di specificare cosa manca
  q6_2.setRequired(true);

  // ================= ITEM #3 =================
  var pageBreak = form.addPageBreakItem();
  pageBreak.setTitle("Item #3 — [Numerical Corruption] (page_number_information - C1)");
  pageBreak.setHelpText("❓ DOMANDA CORROTTA: \"In the table on page1of8 what were the salaries and wages for year five?\"\n📌 DOMANDA ORIGINALE: \"In the table on page 7 what were the salaries and wages for year five?\"\n\n⚖️ DECISIONE AGENTE: UNANSWERABLE | CAUSA PRIMARIA: SPATIAL_MISMATCH\n💬 RISPOSTA FINALE: \"Unable to determine\"\n\n📝 SPIEGAZIONE DELLA CAUSA:\n\"The question incorrectly specifies that the required data is located on page 1. The correct table containing 'Salaries and Wages' and 'Year 5' is found on page 2, where the value is $272,938.\"\n\n🔍 EVIDENZE ESTRATTE DAL DOCUMENTO: [p.2 Q2] Salaries and Wages | $272,938\n⚙️ PROMPT USATI: question_analysis_v1, layout_v4");

  var q1_3 = form.addMultipleChoiceItem();
  q1_3.setTitle("#3.1 - La spiegazione circa la causa di unanswerability è corretta?");
  q1_3.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q1_3.setRequired(true);

  var q2_3 = form.addMultipleChoiceItem();
  q2_3.setTitle("#3.2 - La spiegazione circa la causa di unanswerability è completa?");
  q2_3.setChoiceValues(["Sì", "No"]);
  q2_3.showOtherOption(true); // Permette di specificare cosa manca
  q2_3.setRequired(true);

  var q3_3 = form.addMultipleChoiceItem();
  q3_3.setTitle("#3.3 - La spiegazione contiene riferimenti corretti alle parti di documento coinvolte?");
  q3_3.setChoiceValues(["Sì", "No", "Parzialmente", "Non applicabile (nessun riferimento necessario)"]);
  q3_3.setRequired(true);

  var q4_3 = form.addMultipleChoiceItem();
  q4_3.setTitle("#3.4 - La spiegazione contiene tutti i riferimenti completi alle parti di documento coinvolte?");
  q4_3.setChoiceValues(["Sì", "No", "Non applicabile"]);
  q4_3.showOtherOption(true); // Permette di specificare cosa manca
  q4_3.setRequired(true);

  var q5_3 = form.addMultipleChoiceItem();
  q5_3.setTitle("#3.5 - La spiegazione contiene riferimenti corretti alle parti di domanda che sono causa di unanswerability?");
  q5_3.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q5_3.setRequired(true);

  var q6_3 = form.addMultipleChoiceItem();
  q6_3.setTitle("#3.6 - La spiegazione contiene tutti i riferimenti completi alle parti di domanda che sono causa di unanswerability?");
  q6_3.setChoiceValues(["Sì", "No"]);
  q6_3.showOtherOption(true); // Permette di specificare cosa manca
  q6_3.setRequired(true);

  // ================= ITEM #4 =================
  var pageBreak = form.addPageBreakItem();
  pageBreak.setTitle("Item #4 — [Numerical Corruption] (percentage - C2)");
  pageBreak.setHelpText("❓ DOMANDA CORROTTA: \"What is the enrollment percentage of white government?\"\n📌 DOMANDA ORIGINALE: \"HOW MANY PERCENTAGE OF WHITE COUNTRY IN STATATE?\"\n\n⚖️ DECISIONE AGENTE: INSUFFICIENT_EVIDENCE | CAUSA PRIMARIA: None\n💬 RISPOSTA FINALE: \"Unable to determine\"\n\n📝 SPIEGAZIONE DELLA CAUSA:\n\"The phrase 'white government' does not appear anywhere in the document. The document provides demographic data based on standard racial/ethnic categories, meaning the issue is a content mismatch (entity not found), not a spatial mismatch.\"\n\n🔍 EVIDENZE ESTRATTE DAL DOCUMENTO: (Nessuna evidenza estratta)\n⚙️ PROMPT USATI: question_analysis_v1, layout_v4, layout_v4, nlp_tag_cot, docel_cot_v4, answerability_verifier_v1, nlp_tag_cot");

  var q1_4 = form.addMultipleChoiceItem();
  q1_4.setTitle("#4.1 - La spiegazione circa la causa di unanswerability è corretta?");
  q1_4.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q1_4.setRequired(true);

  var q2_4 = form.addMultipleChoiceItem();
  q2_4.setTitle("#4.2 - La spiegazione circa la causa di unanswerability è completa?");
  q2_4.setChoiceValues(["Sì", "No"]);
  q2_4.showOtherOption(true); // Permette di specificare cosa manca
  q2_4.setRequired(true);

  var q3_4 = form.addMultipleChoiceItem();
  q3_4.setTitle("#4.3 - La spiegazione contiene riferimenti corretti alle parti di documento coinvolte?");
  q3_4.setChoiceValues(["Sì", "No", "Parzialmente", "Non applicabile (nessun riferimento necessario)"]);
  q3_4.setRequired(true);

  var q4_4 = form.addMultipleChoiceItem();
  q4_4.setTitle("#4.4 - La spiegazione contiene tutti i riferimenti completi alle parti di documento coinvolte?");
  q4_4.setChoiceValues(["Sì", "No", "Non applicabile"]);
  q4_4.showOtherOption(true); // Permette di specificare cosa manca
  q4_4.setRequired(true);

  var q5_4 = form.addMultipleChoiceItem();
  q5_4.setTitle("#4.5 - La spiegazione contiene riferimenti corretti alle parti di domanda che sono causa di unanswerability?");
  q5_4.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q5_4.setRequired(true);

  var q6_4 = form.addMultipleChoiceItem();
  q6_4.setTitle("#4.6 - La spiegazione contiene tutti i riferimenti completi alle parti di domanda che sono causa di unanswerability?");
  q6_4.setChoiceValues(["Sì", "No"]);
  q6_4.showOtherOption(true); // Permette di specificare cosa manca
  q6_4.setRequired(true);

  // ================= ITEM #5 =================
  var pageBreak = form.addPageBreakItem();
  pageBreak.setTitle("Item #5 — [Numerical Corruption] (price_numerical_value - C1)");
  pageBreak.setHelpText("❓ DOMANDA CORROTTA: \"What is the fair market value of the property?\"\n📌 DOMANDA ORIGINALE: \"What is the purchase price of the property?\"\n\n⚖️ DECISIONE AGENTE: INSUFFICIENT_EVIDENCE | CAUSA PRIMARIA: None\n💬 RISPOSTA FINALE: \"Unable to determine\"\n\n📝 SPIEGAZIONE DELLA CAUSA:\n\"The document does not explicitly state the 'fair market value' of the property, nor is a corresponding monetary value visible across the provided pages.\"\n\n🔍 EVIDENZE ESTRATTE DAL DOCUMENTO: (Nessuna evidenza estratta)\n⚙️ PROMPT USATI: question_analysis_v1, layout_v4, layout_v4, nlp_tag_cot, docel_cot_v4, answerability_verifier_v1, nlp_tag_cot");

  var q1_5 = form.addMultipleChoiceItem();
  q1_5.setTitle("#5.1 - La spiegazione circa la causa di unanswerability è corretta?");
  q1_5.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q1_5.setRequired(true);

  var q2_5 = form.addMultipleChoiceItem();
  q2_5.setTitle("#5.2 - La spiegazione circa la causa di unanswerability è completa?");
  q2_5.setChoiceValues(["Sì", "No"]);
  q2_5.showOtherOption(true); // Permette di specificare cosa manca
  q2_5.setRequired(true);

  var q3_5 = form.addMultipleChoiceItem();
  q3_5.setTitle("#5.3 - La spiegazione contiene riferimenti corretti alle parti di documento coinvolte?");
  q3_5.setChoiceValues(["Sì", "No", "Parzialmente", "Non applicabile (nessun riferimento necessario)"]);
  q3_5.setRequired(true);

  var q4_5 = form.addMultipleChoiceItem();
  q4_5.setTitle("#5.4 - La spiegazione contiene tutti i riferimenti completi alle parti di documento coinvolte?");
  q4_5.setChoiceValues(["Sì", "No", "Non applicabile"]);
  q4_5.showOtherOption(true); // Permette di specificare cosa manca
  q4_5.setRequired(true);

  var q5_5 = form.addMultipleChoiceItem();
  q5_5.setTitle("#5.5 - La spiegazione contiene riferimenti corretti alle parti di domanda che sono causa di unanswerability?");
  q5_5.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q5_5.setRequired(true);

  var q6_5 = form.addMultipleChoiceItem();
  q6_5.setTitle("#5.6 - La spiegazione contiene tutti i riferimenti completi alle parti di domanda che sono causa di unanswerability?");
  q6_5.setChoiceValues(["Sì", "No"]);
  q6_5.showOtherOption(true); // Permette di specificare cosa manca
  q6_5.setRequired(true);

  // ================= ITEM #6 =================
  var pageBreak = form.addPageBreakItem();
  pageBreak.setTitle("Item #6 — [Numerical Corruption] (temperature - C1)");
  pageBreak.setHelpText("❓ DOMANDA CORROTTA: \"What is the highest temperature recorded?\"\n📌 DOMANDA ORIGINALE: \"What are the temperatures in Image?\"\n\n⚖️ DECISIONE AGENTE: UNANSWERABLE | CAUSA PRIMARIA: DOCUMENT_ELEMENT_MISMATCH\n💬 RISPOSTA FINALE: \"Unable to determine\"\n\n📝 SPIEGAZIONE DELLA CAUSA:\n\"Although the document discusses temperature change and mentions that the last decade was the warmest on record, it does not provide a single, explicit numerical value labeled as the 'highest temperature recorded,' making the answer unanswerable based on a specific document element.\"\n\n🔍 EVIDENZE ESTRATTE DAL DOCUMENTO: [p.1 Q3] Temperature change (°F)... The last decade was the warmest on record throughout the West.\n⚙️ PROMPT USATI: question_analysis_v1, layout_v4, layout_v4");

  var q1_6 = form.addMultipleChoiceItem();
  q1_6.setTitle("#6.1 - La spiegazione circa la causa di unanswerability è corretta?");
  q1_6.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q1_6.setRequired(true);

  var q2_6 = form.addMultipleChoiceItem();
  q2_6.setTitle("#6.2 - La spiegazione circa la causa di unanswerability è completa?");
  q2_6.setChoiceValues(["Sì", "No"]);
  q2_6.showOtherOption(true); // Permette di specificare cosa manca
  q2_6.setRequired(true);

  var q3_6 = form.addMultipleChoiceItem();
  q3_6.setTitle("#6.3 - La spiegazione contiene riferimenti corretti alle parti di documento coinvolte?");
  q3_6.setChoiceValues(["Sì", "No", "Parzialmente", "Non applicabile (nessun riferimento necessario)"]);
  q3_6.setRequired(true);

  var q4_6 = form.addMultipleChoiceItem();
  q4_6.setTitle("#6.4 - La spiegazione contiene tutti i riferimenti completi alle parti di documento coinvolte?");
  q4_6.setChoiceValues(["Sì", "No", "Non applicabile"]);
  q4_6.showOtherOption(true); // Permette di specificare cosa manca
  q4_6.setRequired(true);

  var q5_6 = form.addMultipleChoiceItem();
  q5_6.setTitle("#6.5 - La spiegazione contiene riferimenti corretti alle parti di domanda che sono causa di unanswerability?");
  q5_6.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q5_6.setRequired(true);

  var q6_6 = form.addMultipleChoiceItem();
  q6_6.setTitle("#6.6 - La spiegazione contiene tutti i riferimenti completi alle parti di domanda che sono causa di unanswerability?");
  q6_6.setChoiceValues(["Sì", "No"]);
  q6_6.showOtherOption(true); // Permette di specificare cosa manca
  q6_6.setRequired(true);

  // ================= ITEM #7 =================
  var pageBreak = form.addPageBreakItem();
  pageBreak.setTitle("Item #7 — [Numerical Corruption] (time_numerical_value - C2)");
  pageBreak.setHelpText("❓ DOMANDA CORROTTA: \"On page six, what event from 20 years is included in the attachment to the second to last question?\"\n📌 DOMANDA ORIGINALE: \"On page six, what month is included in the answer to the second to last question?\"\n\n⚖️ DECISIONE AGENTE: INSUFFICIENT_EVIDENCE | CAUSA PRIMARIA: None\n💬 RISPOSTA FINALE: \"Unable to determine\"\n\n📝 SPIEGAZIONE DELLA CAUSA:\n\"The question asks for an event from 20 years in the attachment to the second to last question on page six. While page six contains the second to last question (Q14), the visible content does not include any attachment or text describing an event from 20 years in relation to this question.\"\n\n🔍 EVIDENZE ESTRATTE DAL DOCUMENTO: (Nessuna evidenza estratta)\n⚙️ PROMPT USATI: question_analysis_v1, layout_v4, nlp_tag_cot, docel_cot_v4, docel_cot_v4, answerability_verifier_v1, nlp_tag_cot");

  var q1_7 = form.addMultipleChoiceItem();
  q1_7.setTitle("#7.1 - La spiegazione circa la causa di unanswerability è corretta?");
  q1_7.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q1_7.setRequired(true);

  var q2_7 = form.addMultipleChoiceItem();
  q2_7.setTitle("#7.2 - La spiegazione circa la causa di unanswerability è completa?");
  q2_7.setChoiceValues(["Sì", "No"]);
  q2_7.showOtherOption(true); // Permette di specificare cosa manca
  q2_7.setRequired(true);

  var q3_7 = form.addMultipleChoiceItem();
  q3_7.setTitle("#7.3 - La spiegazione contiene riferimenti corretti alle parti di documento coinvolte?");
  q3_7.setChoiceValues(["Sì", "No", "Parzialmente", "Non applicabile (nessun riferimento necessario)"]);
  q3_7.setRequired(true);

  var q4_7 = form.addMultipleChoiceItem();
  q4_7.setTitle("#7.4 - La spiegazione contiene tutti i riferimenti completi alle parti di documento coinvolte?");
  q4_7.setChoiceValues(["Sì", "No", "Non applicabile"]);
  q4_7.showOtherOption(true); // Permette di specificare cosa manca
  q4_7.setRequired(true);

  var q5_7 = form.addMultipleChoiceItem();
  q5_7.setTitle("#7.5 - La spiegazione contiene riferimenti corretti alle parti di domanda che sono causa di unanswerability?");
  q5_7.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q5_7.setRequired(true);

  var q6_7 = form.addMultipleChoiceItem();
  q6_7.setTitle("#7.6 - La spiegazione contiene tutti i riferimenti completi alle parti di domanda che sono causa di unanswerability?");
  q6_7.setChoiceValues(["Sì", "No"]);
  q6_7.showOtherOption(true); // Permette di specificare cosa manca
  q6_7.setRequired(true);

  // ================= ITEM #8 =================
  var pageBreak = form.addPageBreakItem();
  pageBreak.setTitle("Item #8 — [Numerical Corruption] (year_number_information - C2)");
  pageBreak.setHelpText("❓ DOMANDA CORROTTA: \"What is the issue date of the Federal Register, Volume 77 Issue 2015 Chapter III?\"\n📌 DOMANDA ORIGINALE: \"What is the issue date of the Federal Register, Volume 77 Issue 230 ?\"\n\n⚖️ DECISIONE AGENTE: UNANSWERABLE | CAUSA PRIMARIA: SPATIAL_MISMATCH\n💬 RISPOSTA FINALE: \"Unable to determine\"\n\n📝 SPIEGAZIONE DELLA CAUSA:\n\"The document header clearly states the issue date is November 29, 2012, for Issue 230, which does not match the requested Issue 2015.\"\n\n🔍 EVIDENZE ESTRATTE DAL DOCUMENTO: [p.1 Q1] Federal Register, Volume 77 Issue 230 (Thursday, November 29, 2012)\n⚙️ PROMPT USATI: question_analysis_v1, layout_v4");

  var q1_8 = form.addMultipleChoiceItem();
  q1_8.setTitle("#8.1 - La spiegazione circa la causa di unanswerability è corretta?");
  q1_8.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q1_8.setRequired(true);

  var q2_8 = form.addMultipleChoiceItem();
  q2_8.setTitle("#8.2 - La spiegazione circa la causa di unanswerability è completa?");
  q2_8.setChoiceValues(["Sì", "No"]);
  q2_8.showOtherOption(true); // Permette di specificare cosa manca
  q2_8.setRequired(true);

  var q3_8 = form.addMultipleChoiceItem();
  q3_8.setTitle("#8.3 - La spiegazione contiene riferimenti corretti alle parti di documento coinvolte?");
  q3_8.setChoiceValues(["Sì", "No", "Parzialmente", "Non applicabile (nessun riferimento necessario)"]);
  q3_8.setRequired(true);

  var q4_8 = form.addMultipleChoiceItem();
  q4_8.setTitle("#8.4 - La spiegazione contiene tutti i riferimenti completi alle parti di documento coinvolte?");
  q4_8.setChoiceValues(["Sì", "No", "Non applicabile"]);
  q4_8.showOtherOption(true); // Permette di specificare cosa manca
  q4_8.setRequired(true);

  var q5_8 = form.addMultipleChoiceItem();
  q5_8.setTitle("#8.5 - La spiegazione contiene riferimenti corretti alle parti di domanda che sono causa di unanswerability?");
  q5_8.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q5_8.setRequired(true);

  var q6_8 = form.addMultipleChoiceItem();
  q6_8.setTitle("#8.6 - La spiegazione contiene tutti i riferimenti completi alle parti di domanda che sono causa di unanswerability?");
  q6_8.setChoiceValues(["Sì", "No"]);
  q6_8.showOtherOption(true); // Permette di specificare cosa manca
  q6_8.setRequired(true);

  // ================= ITEM #9 =================
  var pageBreak = form.addPageBreakItem();
  pageBreak.setTitle("Item #9 — [Numerical Corruption] (year_numerical_value - C1)");
  pageBreak.setHelpText("❓ DOMANDA CORROTTA: \"What is the budget for the Council Agenda Office in FY 2020-21?\"\n📌 DOMANDA ORIGINALE: \"What is the FY 2020-2021 budget for the Council Agenda Office?\"\n\n⚖️ DECISIONE AGENTE: ANSWERABLE | CAUSA PRIMARIA: None\n💬 RISPOSTA FINALE: \"1,152,990\"\n\n📝 SPIEGAZIONE DELLA CAUSA:\n\"The budget for the Council Agenda Office in FY 2020-21 is clearly visible and extractable from the main expense table in the document.\"\n\n🔍 EVIDENZE ESTRATTE DAL DOCUMENTO: (Nessuna evidenza estratta)\n⚙️ PROMPT USATI: question_analysis_v1, layout_v4, layout_v4, nlp_tag_cot, nlp_tag_cot, answerability_verifier_v1, nlp_tag_cot");

  var q1_9 = form.addMultipleChoiceItem();
  q1_9.setTitle("#9.1 - La spiegazione circa la causa di unanswerability è corretta?");
  q1_9.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q1_9.setRequired(true);

  var q2_9 = form.addMultipleChoiceItem();
  q2_9.setTitle("#9.2 - La spiegazione circa la causa di unanswerability è completa?");
  q2_9.setChoiceValues(["Sì", "No"]);
  q2_9.showOtherOption(true); // Permette di specificare cosa manca
  q2_9.setRequired(true);

  var q3_9 = form.addMultipleChoiceItem();
  q3_9.setTitle("#9.3 - La spiegazione contiene riferimenti corretti alle parti di documento coinvolte?");
  q3_9.setChoiceValues(["Sì", "No", "Parzialmente", "Non applicabile (nessun riferimento necessario)"]);
  q3_9.setRequired(true);

  var q4_9 = form.addMultipleChoiceItem();
  q4_9.setTitle("#9.4 - La spiegazione contiene tutti i riferimenti completi alle parti di documento coinvolte?");
  q4_9.setChoiceValues(["Sì", "No", "Non applicabile"]);
  q4_9.showOtherOption(true); // Permette di specificare cosa manca
  q4_9.setRequired(true);

  var q5_9 = form.addMultipleChoiceItem();
  q5_9.setTitle("#9.5 - La spiegazione contiene riferimenti corretti alle parti di domanda che sono causa di unanswerability?");
  q5_9.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q5_9.setRequired(true);

  var q6_9 = form.addMultipleChoiceItem();
  q6_9.setTitle("#9.6 - La spiegazione contiene tutti i riferimenti completi alle parti di domanda che sono causa di unanswerability?");
  q6_9.setChoiceValues(["Sì", "No"]);
  q6_9.showOtherOption(true); // Permette di specificare cosa manca
  q6_9.setRequired(true);

  // ================= ITEM #10 =================
  var pageBreak = form.addPageBreakItem();
  pageBreak.setTitle("Item #10 — [Numerical Corruption] (measure_unit - C1)");
  pageBreak.setHelpText("❓ DOMANDA CORROTTA: \"What is centi. ft. converted to 4 N.m in the metric conversion chart?\"\n📌 DOMANDA ORIGINALE: \"What is 60 lbs. ft. converted to 4 N.m in the metric conversion chart?\"\n\n⚖️ DECISIONE AGENTE: UNANSWERABLE | CAUSA PRIMARIA: SPATIAL_MISMATCH\n💬 RISPOSTA FINALE: \"Unable to determine\"\n\n📝 SPIEGAZIONE DELLA CAUSA:\n\"The document contains metric conversion charts (e.g., lb. ft. to N.m and kg-cm to N.m), but none of the charts provide a conversion for 'centi. ft.' to N.m, making the requested information spatially mismatched.\"\n\n🔍 EVIDENZE ESTRATTE DAL DOCUMENTO: [p.2 Q3] METRIC CONVERSION: lb. ft. to N.m | [p.4 Q3] METRIC CONVERSION: kg-cm to N.m\n⚙️ PROMPT USATI: question_analysis_v1, layout_v4");

  var q1_10 = form.addMultipleChoiceItem();
  q1_10.setTitle("#10.1 - La spiegazione circa la causa di unanswerability è corretta?");
  q1_10.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q1_10.setRequired(true);

  var q2_10 = form.addMultipleChoiceItem();
  q2_10.setTitle("#10.2 - La spiegazione circa la causa di unanswerability è completa?");
  q2_10.setChoiceValues(["Sì", "No"]);
  q2_10.showOtherOption(true); // Permette di specificare cosa manca
  q2_10.setRequired(true);

  var q3_10 = form.addMultipleChoiceItem();
  q3_10.setTitle("#10.3 - La spiegazione contiene riferimenti corretti alle parti di documento coinvolte?");
  q3_10.setChoiceValues(["Sì", "No", "Parzialmente", "Non applicabile (nessun riferimento necessario)"]);
  q3_10.setRequired(true);

  var q4_10 = form.addMultipleChoiceItem();
  q4_10.setTitle("#10.4 - La spiegazione contiene tutti i riferimenti completi alle parti di documento coinvolte?");
  q4_10.setChoiceValues(["Sì", "No", "Non applicabile"]);
  q4_10.showOtherOption(true); // Permette di specificare cosa manca
  q4_10.setRequired(true);

  var q5_10 = form.addMultipleChoiceItem();
  q5_10.setTitle("#10.5 - La spiegazione contiene riferimenti corretti alle parti di domanda che sono causa di unanswerability?");
  q5_10.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q5_10.setRequired(true);

  var q6_10 = form.addMultipleChoiceItem();
  q6_10.setTitle("#10.6 - La spiegazione contiene tutti i riferimenti completi alle parti di domanda che sono causa di unanswerability?");
  q6_10.setChoiceValues(["Sì", "No"]);
  q6_10.showOtherOption(true); // Permette di specificare cosa manca
  q6_10.setRequired(true);

  // ================= ITEM #11 =================
  var pageBreak = form.addPageBreakItem();
  pageBreak.setTitle("Item #11 — [Temporal Corruption] (date_information - C1)");
  pageBreak.setHelpText("❓ DOMANDA CORROTTA: \"What is scheduled in the morning on May 1st, as per the time table?\"\n📌 DOMANDA ORIGINALE: \"What is scheduled in the morning on Tuesday, June 12th, as per the time table?\"\n\n⚖️ DECISIONE AGENTE: UNANSWERABLE | CAUSA PRIMARIA: SPATIAL_MISMATCH\n💬 RISPOSTA FINALE: \"Unable to determine\"\n\n📝 SPIEGAZIONE DELLA CAUSA:\n\"The time table is the correct location for the answer, but the document only provides dates in June, making the requested date of May 1st spatially unavailable.\"\n\n🔍 EVIDENZE ESTRATTE DAL DOCUMENTO: [p.1 Q3] ANNUAL DEPARTMENTAL EXAMINATIONS 1956 TIME-TABLE Date Time Examination Tuesday 1st June 9.30 - 11.30 Wednesday 2nd June 9.30 - 11.30 Thursday 3rd June 9.30 - 11.30 Friday 4th June 9.30 - 11.30 Saturday 5th June 9.30 - 11.30 Monday 7th June 9.30 - 11.30 Tuesday 8th June 9.30 - 11.30 Wednesday 9th June 9.30 - 11.30 Thursday 10th June 9.30 - 11.30 Friday 11th June 9.30 - 11.30\n⚙️ PROMPT USATI: question_analysis_v1, layout_v4");

  var q1_11 = form.addMultipleChoiceItem();
  q1_11.setTitle("#11.1 - La spiegazione circa la causa di unanswerability è corretta?");
  q1_11.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q1_11.setRequired(true);

  var q2_11 = form.addMultipleChoiceItem();
  q2_11.setTitle("#11.2 - La spiegazione circa la causa di unanswerability è completa?");
  q2_11.setChoiceValues(["Sì", "No"]);
  q2_11.showOtherOption(true); // Permette di specificare cosa manca
  q2_11.setRequired(true);

  var q3_11 = form.addMultipleChoiceItem();
  q3_11.setTitle("#11.3 - La spiegazione contiene riferimenti corretti alle parti di documento coinvolte?");
  q3_11.setChoiceValues(["Sì", "No", "Parzialmente", "Non applicabile (nessun riferimento necessario)"]);
  q3_11.setRequired(true);

  var q4_11 = form.addMultipleChoiceItem();
  q4_11.setTitle("#11.4 - La spiegazione contiene tutti i riferimenti completi alle parti di documento coinvolte?");
  q4_11.setChoiceValues(["Sì", "No", "Non applicabile"]);
  q4_11.showOtherOption(true); // Permette di specificare cosa manca
  q4_11.setRequired(true);

  var q5_11 = form.addMultipleChoiceItem();
  q5_11.setTitle("#11.5 - La spiegazione contiene riferimenti corretti alle parti di domanda che sono causa di unanswerability?");
  q5_11.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q5_11.setRequired(true);

  var q6_11 = form.addMultipleChoiceItem();
  q6_11.setTitle("#11.6 - La spiegazione contiene tutti i riferimenti completi alle parti di domanda che sono causa di unanswerability?");
  q6_11.setChoiceValues(["Sì", "No"]);
  q6_11.showOtherOption(true); // Permette di specificare cosa manca
  q6_11.setRequired(true);

  // ================= ITEM #12 =================
  var pageBreak = form.addPageBreakItem();
  pageBreak.setTitle("Item #12 — [Temporal Corruption] (time_information - C1)");
  pageBreak.setHelpText("❓ DOMANDA CORROTTA: \"What is the duration of the video still shown in Figure 3, measured in 24 hours a day?\"\n📌 DOMANDA ORIGINALE: \"What is the duration of the video still shown in Figure 3?\"\n\n⚖️ DECISIONE AGENTE: INSUFFICIENT_EVIDENCE | CAUSA PRIMARIA: None\n💬 RISPOSTA FINALE: \"Unable to determine\"\n\n📝 SPIEGAZIONE DELLA CAUSA:\n\"Although Figure 3 is visible on page 2, the document does not state the duration of the video still in terms of '24 hours a day.' The timestamps visible on the figures refer to the time within the video clip, not its overall duration.\"\n\n🔍 EVIDENZE ESTRATTE DAL DOCUMENTO: (Nessuna evidenza estratta)\n⚙️ PROMPT USATI: question_analysis_v1, layout_v4, layout_v4, nlp_tag_cot, nlp_tag_cot, answerability_verifier_v1, nlp_tag_cot");

  var q1_12 = form.addMultipleChoiceItem();
  q1_12.setTitle("#12.1 - La spiegazione circa la causa di unanswerability è corretta?");
  q1_12.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q1_12.setRequired(true);

  var q2_12 = form.addMultipleChoiceItem();
  q2_12.setTitle("#12.2 - La spiegazione circa la causa di unanswerability è completa?");
  q2_12.setChoiceValues(["Sì", "No"]);
  q2_12.showOtherOption(true); // Permette di specificare cosa manca
  q2_12.setRequired(true);

  var q3_12 = form.addMultipleChoiceItem();
  q3_12.setTitle("#12.3 - La spiegazione contiene riferimenti corretti alle parti di documento coinvolte?");
  q3_12.setChoiceValues(["Sì", "No", "Parzialmente", "Non applicabile (nessun riferimento necessario)"]);
  q3_12.setRequired(true);

  var q4_12 = form.addMultipleChoiceItem();
  q4_12.setTitle("#12.4 - La spiegazione contiene tutti i riferimenti completi alle parti di documento coinvolte?");
  q4_12.setChoiceValues(["Sì", "No", "Non applicabile"]);
  q4_12.showOtherOption(true); // Permette di specificare cosa manca
  q4_12.setRequired(true);

  var q5_12 = form.addMultipleChoiceItem();
  q5_12.setTitle("#12.5 - La spiegazione contiene riferimenti corretti alle parti di domanda che sono causa di unanswerability?");
  q5_12.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q5_12.setRequired(true);

  var q6_12 = form.addMultipleChoiceItem();
  q6_12.setTitle("#12.6 - La spiegazione contiene tutti i riferimenti completi alle parti di domanda che sono causa di unanswerability?");
  q6_12.setChoiceValues(["Sì", "No"]);
  q6_12.showOtherOption(true); // Permette di specificare cosa manca
  q6_12.setRequired(true);

  // ================= ITEM #13 =================
  var pageBreak = form.addPageBreakItem();
  pageBreak.setTitle("Item #13 — [Temporal Corruption] (time_information - C3)");
  pageBreak.setHelpText("❓ DOMANDA CORROTTA: \"What is the cost for the current state of the experiment with Facebook ads and Mailchimp?\"\n📌 DOMANDA ORIGINALE: \"What is the cost for duration of experiment Facebook ads and twitter ?\"\n\n⚖️ DECISIONE AGENTE: UNANSWERABLE | CAUSA PRIMARIA: SPATIAL_MISMATCH\n💬 RISPOSTA FINALE: \"Unable to determine\"\n\n📝 SPIEGAZIONE DELLA CAUSA:\n\"The document only provides a specific cost for Mailchimp ($75/mo) in the context of Facebook posts, but it does not provide a separate or combined cost for the actual Facebook advertising spend, making the total cost unanswerable.\"\n\n🔍 EVIDENZE ESTRATTE DAL DOCUMENTO: [p.1 Q3] Facebook Posts (WBUR) ... $75/mo for Mailchimp\n⚙️ PROMPT USATI: question_analysis_v1, layout_v4");

  var q1_13 = form.addMultipleChoiceItem();
  q1_13.setTitle("#13.1 - La spiegazione circa la causa di unanswerability è corretta?");
  q1_13.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q1_13.setRequired(true);

  var q2_13 = form.addMultipleChoiceItem();
  q2_13.setTitle("#13.2 - La spiegazione circa la causa di unanswerability è completa?");
  q2_13.setChoiceValues(["Sì", "No"]);
  q2_13.showOtherOption(true); // Permette di specificare cosa manca
  q2_13.setRequired(true);

  var q3_13 = form.addMultipleChoiceItem();
  q3_13.setTitle("#13.3 - La spiegazione contiene riferimenti corretti alle parti di documento coinvolte?");
  q3_13.setChoiceValues(["Sì", "No", "Parzialmente", "Non applicabile (nessun riferimento necessario)"]);
  q3_13.setRequired(true);

  var q4_13 = form.addMultipleChoiceItem();
  q4_13.setTitle("#13.4 - La spiegazione contiene tutti i riferimenti completi alle parti di documento coinvolte?");
  q4_13.setChoiceValues(["Sì", "No", "Non applicabile"]);
  q4_13.showOtherOption(true); // Permette di specificare cosa manca
  q4_13.setRequired(true);

  var q5_13 = form.addMultipleChoiceItem();
  q5_13.setTitle("#13.5 - La spiegazione contiene riferimenti corretti alle parti di domanda che sono causa di unanswerability?");
  q5_13.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q5_13.setRequired(true);

  var q6_13 = form.addMultipleChoiceItem();
  q6_13.setTitle("#13.6 - La spiegazione contiene tutti i riferimenti completi alle parti di domanda che sono causa di unanswerability?");
  q6_13.setChoiceValues(["Sì", "No"]);
  q6_13.showOtherOption(true); // Permette di specificare cosa manca
  q6_13.setRequired(true);

  // ================= ITEM #14 =================
  var pageBreak = form.addPageBreakItem();
  pageBreak.setTitle("Item #14 — [Temporal Corruption] (time_information - C2)");
  pageBreak.setHelpText("❓ DOMANDA CORROTTA: \"Which are the holidays in 2010 when most people were killed in alcohol-impaired driving?\"\n📌 DOMANDA ORIGINALE: \"Which are the holidays in 2009 when most people were killed in alcohol-impaired driving?\"\n\n⚖️ DECISIONE AGENTE: UNANSWERABLE | CAUSA PRIMARIA: SPATIAL_MISMATCH\n💬 RISPOSTA FINALE: \"Unable to determine\"\n\n📝 SPIEGAZIONE DELLA CAUSA:\n\"The document contains statistics regarding holidays and alcohol-impaired driving deaths, but all the specific data provided is for the year 2009, not the requested year 2010.\"\n\n🔍 EVIDENZE ESTRATTE DAL DOCUMENTO: [p.1 Q3] In 2009, the holidays on which alcohol-related crashes represented the highest percentage of total fatalities were Memorial Day (42 percent), New Year's Day and the Fourth of July (40 percent), and Labor Day (38 percent).\n⚙️ PROMPT USATI: question_analysis_v1, layout_v4");

  var q1_14 = form.addMultipleChoiceItem();
  q1_14.setTitle("#14.1 - La spiegazione circa la causa di unanswerability è corretta?");
  q1_14.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q1_14.setRequired(true);

  var q2_14 = form.addMultipleChoiceItem();
  q2_14.setTitle("#14.2 - La spiegazione circa la causa di unanswerability è completa?");
  q2_14.setChoiceValues(["Sì", "No"]);
  q2_14.showOtherOption(true); // Permette di specificare cosa manca
  q2_14.setRequired(true);

  var q3_14 = form.addMultipleChoiceItem();
  q3_14.setTitle("#14.3 - La spiegazione contiene riferimenti corretti alle parti di documento coinvolte?");
  q3_14.setChoiceValues(["Sì", "No", "Parzialmente", "Non applicabile (nessun riferimento necessario)"]);
  q3_14.setRequired(true);

  var q4_14 = form.addMultipleChoiceItem();
  q4_14.setTitle("#14.4 - La spiegazione contiene tutti i riferimenti completi alle parti di documento coinvolte?");
  q4_14.setChoiceValues(["Sì", "No", "Non applicabile"]);
  q4_14.showOtherOption(true); // Permette di specificare cosa manca
  q4_14.setRequired(true);

  var q5_14 = form.addMultipleChoiceItem();
  q5_14.setTitle("#14.5 - La spiegazione contiene riferimenti corretti alle parti di domanda che sono causa di unanswerability?");
  q5_14.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q5_14.setRequired(true);

  var q6_14 = form.addMultipleChoiceItem();
  q6_14.setTitle("#14.6 - La spiegazione contiene tutti i riferimenti completi alle parti di domanda che sono causa di unanswerability?");
  q6_14.setChoiceValues(["Sì", "No"]);
  q6_14.showOtherOption(true); // Permette di specificare cosa manca
  q6_14.setRequired(true);

  // ================= ITEM #15 =================
  var pageBreak = form.addPageBreakItem();
  pageBreak.setTitle("Item #15 — [Temporal Corruption] (time_information - C1)");
  pageBreak.setHelpText("❓ DOMANDA CORROTTA: \"What is the next year you will have a day of the week?\"\n📌 DOMANDA ORIGINALE: \"What is the next year you will have an extra week?\"\n\n⚖️ DECISIONE AGENTE: INSUFFICIENT_EVIDENCE | CAUSA PRIMARIA: None\n💬 RISPOSTA FINALE: \"Unable to determine\"\n\n📝 SPIEGAZIONE DELLA CAUSA:\n\"The document is empty and contains no textual evidence regarding dates or years, making it impossible to confirm or reject the candidate cause of a value mismatch.\"\n\n🔍 EVIDENZE ESTRATTE DAL DOCUMENTO: (Nessuna evidenza estratta)\n⚙️ PROMPT USATI: question_analysis_v1, nlp_tag_cot, nlp_tag_cot, docel_cot_v4, nlp_list_ocr_cot, answerability_verifier_v1, nlp_tag_cot");

  var q1_15 = form.addMultipleChoiceItem();
  q1_15.setTitle("#15.1 - La spiegazione circa la causa di unanswerability è corretta?");
  q1_15.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q1_15.setRequired(true);

  var q2_15 = form.addMultipleChoiceItem();
  q2_15.setTitle("#15.2 - La spiegazione circa la causa di unanswerability è completa?");
  q2_15.setChoiceValues(["Sì", "No"]);
  q2_15.showOtherOption(true); // Permette di specificare cosa manca
  q2_15.setRequired(true);

  var q3_15 = form.addMultipleChoiceItem();
  q3_15.setTitle("#15.3 - La spiegazione contiene riferimenti corretti alle parti di documento coinvolte?");
  q3_15.setChoiceValues(["Sì", "No", "Parzialmente", "Non applicabile (nessun riferimento necessario)"]);
  q3_15.setRequired(true);

  var q4_15 = form.addMultipleChoiceItem();
  q4_15.setTitle("#15.4 - La spiegazione contiene tutti i riferimenti completi alle parti di documento coinvolte?");
  q4_15.setChoiceValues(["Sì", "No", "Non applicabile"]);
  q4_15.showOtherOption(true); // Permette di specificare cosa manca
  q4_15.setRequired(true);

  var q5_15 = form.addMultipleChoiceItem();
  q5_15.setTitle("#15.5 - La spiegazione contiene riferimenti corretti alle parti di domanda che sono causa di unanswerability?");
  q5_15.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q5_15.setRequired(true);

  var q6_15 = form.addMultipleChoiceItem();
  q6_15.setTitle("#15.6 - La spiegazione contiene tutti i riferimenti completi alle parti di domanda che sono causa di unanswerability?");
  q6_15.setChoiceValues(["Sì", "No"]);
  q6_15.showOtherOption(true); // Permette di specificare cosa manca
  q6_15.setRequired(true);

  // ================= ITEM #16 =================
  var pageBreak = form.addPageBreakItem();
  pageBreak.setTitle("Item #16 — [Temporal Corruption] (time_information - C1)");
  pageBreak.setHelpText("❓ DOMANDA CORROTTA: \"What is the value 839 of the video still shown in Figure 3?\"\n📌 DOMANDA ORIGINALE: \"What is the duration of the video still shown in Figure 3?\"\n\n⚖️ DECISIONE AGENTE: UNANSWERABLE | CAUSA PRIMARIA: DOCUMENT_ELEMENT_MISMATCH\n💬 RISPOSTA FINALE: \"Unable to determine\"\n\n📝 SPIEGAZIONE DELLA CAUSA:\n\"The question asks for the 'value 839' associated with Figure 3. While Figure 3 is visible on page 3, the number 839 does not appear anywhere in the figure, its caption, or the surrounding text, making the question unanswerable based on the provided document evidence.\"\n\n🔍 EVIDENZE ESTRATTE DAL DOCUMENTO: [p.3 Q2] Figure 3\n⚙️ PROMPT USATI: question_analysis_v1, layout_v4, layout_v4");

  var q1_16 = form.addMultipleChoiceItem();
  q1_16.setTitle("#16.1 - La spiegazione circa la causa di unanswerability è corretta?");
  q1_16.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q1_16.setRequired(true);

  var q2_16 = form.addMultipleChoiceItem();
  q2_16.setTitle("#16.2 - La spiegazione circa la causa di unanswerability è completa?");
  q2_16.setChoiceValues(["Sì", "No"]);
  q2_16.showOtherOption(true); // Permette di specificare cosa manca
  q2_16.setRequired(true);

  var q3_16 = form.addMultipleChoiceItem();
  q3_16.setTitle("#16.3 - La spiegazione contiene riferimenti corretti alle parti di documento coinvolte?");
  q3_16.setChoiceValues(["Sì", "No", "Parzialmente", "Non applicabile (nessun riferimento necessario)"]);
  q3_16.setRequired(true);

  var q4_16 = form.addMultipleChoiceItem();
  q4_16.setTitle("#16.4 - La spiegazione contiene tutti i riferimenti completi alle parti di documento coinvolte?");
  q4_16.setChoiceValues(["Sì", "No", "Non applicabile"]);
  q4_16.showOtherOption(true); // Permette di specificare cosa manca
  q4_16.setRequired(true);

  var q5_16 = form.addMultipleChoiceItem();
  q5_16.setTitle("#16.5 - La spiegazione contiene riferimenti corretti alle parti di domanda che sono causa di unanswerability?");
  q5_16.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q5_16.setRequired(true);

  var q6_16 = form.addMultipleChoiceItem();
  q6_16.setTitle("#16.6 - La spiegazione contiene tutti i riferimenti completi alle parti di domanda che sono causa di unanswerability?");
  q6_16.setChoiceValues(["Sì", "No"]);
  q6_16.showOtherOption(true); // Permette di specificare cosa manca
  q6_16.setRequired(true);

  // ================= ITEM #17 =================
  var pageBreak = form.addPageBreakItem();
  pageBreak.setTitle("Item #17 — [Temporal Corruption] (time_information - C1)");
  pageBreak.setHelpText("❓ DOMANDA CORROTTA: \"Everyday was this document published?\"\n📌 DOMANDA ORIGINALE: \"when did this document published?\"\n\n⚖️ DECISIONE AGENTE: INSUFFICIENT_EVIDENCE | CAUSA PRIMARIA: None\n💬 RISPOSTA FINALE: \"Unable to determine\"\n\n📝 SPIEGAZIONE DELLA CAUSA:\n\"The document only provides a general date (March 2013) and is a roadmap, not a periodical publication. There is no evidence anywhere in the document regarding its publication frequency (daily).\"\n\n🔍 EVIDENZE ESTRATTE DAL DOCUMENTO: (Nessuna evidenza estratta)\n⚙️ PROMPT USATI: question_analysis_v1, layout_v4, nlp_tag_cot, nlp_tag_cot, docel_cot_v4, answerability_verifier_v1, nlp_tag_cot");

  var q1_17 = form.addMultipleChoiceItem();
  q1_17.setTitle("#17.1 - La spiegazione circa la causa di unanswerability è corretta?");
  q1_17.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q1_17.setRequired(true);

  var q2_17 = form.addMultipleChoiceItem();
  q2_17.setTitle("#17.2 - La spiegazione circa la causa di unanswerability è completa?");
  q2_17.setChoiceValues(["Sì", "No"]);
  q2_17.showOtherOption(true); // Permette di specificare cosa manca
  q2_17.setRequired(true);

  var q3_17 = form.addMultipleChoiceItem();
  q3_17.setTitle("#17.3 - La spiegazione contiene riferimenti corretti alle parti di documento coinvolte?");
  q3_17.setChoiceValues(["Sì", "No", "Parzialmente", "Non applicabile (nessun riferimento necessario)"]);
  q3_17.setRequired(true);

  var q4_17 = form.addMultipleChoiceItem();
  q4_17.setTitle("#17.4 - La spiegazione contiene tutti i riferimenti completi alle parti di documento coinvolte?");
  q4_17.setChoiceValues(["Sì", "No", "Non applicabile"]);
  q4_17.showOtherOption(true); // Permette di specificare cosa manca
  q4_17.setRequired(true);

  var q5_17 = form.addMultipleChoiceItem();
  q5_17.setTitle("#17.5 - La spiegazione contiene riferimenti corretti alle parti di domanda che sono causa di unanswerability?");
  q5_17.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q5_17.setRequired(true);

  var q6_17 = form.addMultipleChoiceItem();
  q6_17.setTitle("#17.6 - La spiegazione contiene tutti i riferimenti completi alle parti di domanda che sono causa di unanswerability?");
  q6_17.setChoiceValues(["Sì", "No"]);
  q6_17.showOtherOption(true); // Permette di specificare cosa manca
  q6_17.setRequired(true);

  // ================= ITEM #18 =================
  var pageBreak = form.addPageBreakItem();
  pageBreak.setTitle("Item #18 — [Temporal Corruption] (time_information - C2)");
  pageBreak.setHelpText("❓ DOMANDA CORROTTA: \"Which weeks in 2011 had the most people killed in alcohol-impaired driving?\"\n📌 DOMANDA ORIGINALE: \"Which are the holidays in 2009 when most people were killed in alcohol-impaired driving?\"\n\n⚖️ DECISIONE AGENTE: UNANSWERABLE | CAUSA PRIMARIA: DOCUMENT_ELEMENT_MISMATCH\n💬 RISPOSTA FINALE: \"Unable to determine\"\n\n📝 SPIEGAZIONE DELLA CAUSA:\n\"The question requires weekly data for 2011, but the document only provides general statistics and specific data points for the year 2009, making the answer unanswerable.\"\n\n🔍 EVIDENZE ESTRATTE DAL DOCUMENTO: [p.1 Q1] In 2009, 10,839 people were killed in crashes involving alcohol-impaired drivers in the United States. | [p.1 Q1] In 2009, the fatalities on which alcohol-related crashes represented the highest percentage of total fatalities was Memorial Day (42 percent), New Year's Day and the Fourth of July (40 percent), and Labor Day (38 percent).\n⚙️ PROMPT USATI: question_analysis_v1, layout_v4, layout_v4");

  var q1_18 = form.addMultipleChoiceItem();
  q1_18.setTitle("#18.1 - La spiegazione circa la causa di unanswerability è corretta?");
  q1_18.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q1_18.setRequired(true);

  var q2_18 = form.addMultipleChoiceItem();
  q2_18.setTitle("#18.2 - La spiegazione circa la causa di unanswerability è completa?");
  q2_18.setChoiceValues(["Sì", "No"]);
  q2_18.showOtherOption(true); // Permette di specificare cosa manca
  q2_18.setRequired(true);

  var q3_18 = form.addMultipleChoiceItem();
  q3_18.setTitle("#18.3 - La spiegazione contiene riferimenti corretti alle parti di documento coinvolte?");
  q3_18.setChoiceValues(["Sì", "No", "Parzialmente", "Non applicabile (nessun riferimento necessario)"]);
  q3_18.setRequired(true);

  var q4_18 = form.addMultipleChoiceItem();
  q4_18.setTitle("#18.4 - La spiegazione contiene tutti i riferimenti completi alle parti di documento coinvolte?");
  q4_18.setChoiceValues(["Sì", "No", "Non applicabile"]);
  q4_18.showOtherOption(true); // Permette di specificare cosa manca
  q4_18.setRequired(true);

  var q5_18 = form.addMultipleChoiceItem();
  q5_18.setTitle("#18.5 - La spiegazione contiene riferimenti corretti alle parti di domanda che sono causa di unanswerability?");
  q5_18.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q5_18.setRequired(true);

  var q6_18 = form.addMultipleChoiceItem();
  q6_18.setTitle("#18.6 - La spiegazione contiene tutti i riferimenti completi alle parti di domanda che sono causa di unanswerability?");
  q6_18.setChoiceValues(["Sì", "No"]);
  q6_18.showOtherOption(true); // Permette di specificare cosa manca
  q6_18.setRequired(true);

  // ================= ITEM #19 =================
  var pageBreak = form.addPageBreakItem();
  pageBreak.setTitle("Item #19 — [Temporal Corruption] (time_information - C1)");
  pageBreak.setHelpText("❓ DOMANDA CORROTTA: \"How many days of the month have the 2020-2021?\"\n📌 DOMANDA ORIGINALE: \"How many days of student holidays have the 2020-2021?\"\n\n⚖️ DECISIONE AGENTE: INSUFFICIENT_EVIDENCE | CAUSA PRIMARIA: None\n💬 RISPOSTA FINALE: \"Unable to determine\"\n\n📝 SPIEGAZIONE DELLA CAUSA:\n\"The calendar for the 2020-2021 period is fully visible and detailed across the entire page, meaning the information is spatially present and the cause of mismatch is incorrect.\"\n\n🔍 EVIDENZE ESTRATTE DAL DOCUMENTO: (Nessuna evidenza estratta)\n⚙️ PROMPT USATI: question_analysis_v1, layout_v4, nlp_tag_cot, nlp_tag_cot, docel_cot_v4, answerability_verifier_v1, nlp_tag_cot");

  var q1_19 = form.addMultipleChoiceItem();
  q1_19.setTitle("#19.1 - La spiegazione circa la causa di unanswerability è corretta?");
  q1_19.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q1_19.setRequired(true);

  var q2_19 = form.addMultipleChoiceItem();
  q2_19.setTitle("#19.2 - La spiegazione circa la causa di unanswerability è completa?");
  q2_19.setChoiceValues(["Sì", "No"]);
  q2_19.showOtherOption(true); // Permette di specificare cosa manca
  q2_19.setRequired(true);

  var q3_19 = form.addMultipleChoiceItem();
  q3_19.setTitle("#19.3 - La spiegazione contiene riferimenti corretti alle parti di documento coinvolte?");
  q3_19.setChoiceValues(["Sì", "No", "Parzialmente", "Non applicabile (nessun riferimento necessario)"]);
  q3_19.setRequired(true);

  var q4_19 = form.addMultipleChoiceItem();
  q4_19.setTitle("#19.4 - La spiegazione contiene tutti i riferimenti completi alle parti di documento coinvolte?");
  q4_19.setChoiceValues(["Sì", "No", "Non applicabile"]);
  q4_19.showOtherOption(true); // Permette di specificare cosa manca
  q4_19.setRequired(true);

  var q5_19 = form.addMultipleChoiceItem();
  q5_19.setTitle("#19.5 - La spiegazione contiene riferimenti corretti alle parti di domanda che sono causa di unanswerability?");
  q5_19.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q5_19.setRequired(true);

  var q6_19 = form.addMultipleChoiceItem();
  q6_19.setTitle("#19.6 - La spiegazione contiene tutti i riferimenti completi alle parti di domanda che sono causa di unanswerability?");
  q6_19.setChoiceValues(["Sì", "No"]);
  q6_19.showOtherOption(true); // Permette di specificare cosa manca
  q6_19.setRequired(true);

  // ================= ITEM #20 =================
  var pageBreak = form.addPageBreakItem();
  pageBreak.setTitle("Item #20 — [Temporal Corruption] (time_information - C2)");
  pageBreak.setHelpText("❓ DOMANDA CORROTTA: \"Everyday did this document mention shooting?\"\n📌 DOMANDA ORIGINALE: \"when did this document published?\"\n\n⚖️ DECISIONE AGENTE: INSUFFICIENT_EVIDENCE | CAUSA PRIMARIA: None\n💬 RISPOSTA FINALE: \"Unable to determine\"\n\n📝 SPIEGAZIONE DELLA CAUSA:\n\"The word \"shooting\" does not appear anywhere in the provided document images, making a spatial mismatch irrelevant as the term is entirely absent.\"\n\n🔍 EVIDENZE ESTRATTE DAL DOCUMENTO: [p.7 Q1] shooting\n⚙️ PROMPT USATI: question_analysis_v1, layout_v4, nlp_tag_cot, docel_cot_v4, nlp_list_ocr_cot, nlp_tag_cot");

  var q1_20 = form.addMultipleChoiceItem();
  q1_20.setTitle("#20.1 - La spiegazione circa la causa di unanswerability è corretta?");
  q1_20.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q1_20.setRequired(true);

  var q2_20 = form.addMultipleChoiceItem();
  q2_20.setTitle("#20.2 - La spiegazione circa la causa di unanswerability è completa?");
  q2_20.setChoiceValues(["Sì", "No"]);
  q2_20.showOtherOption(true); // Permette di specificare cosa manca
  q2_20.setRequired(true);

  var q3_20 = form.addMultipleChoiceItem();
  q3_20.setTitle("#20.3 - La spiegazione contiene riferimenti corretti alle parti di documento coinvolte?");
  q3_20.setChoiceValues(["Sì", "No", "Parzialmente", "Non applicabile (nessun riferimento necessario)"]);
  q3_20.setRequired(true);

  var q4_20 = form.addMultipleChoiceItem();
  q4_20.setTitle("#20.4 - La spiegazione contiene tutti i riferimenti completi alle parti di documento coinvolte?");
  q4_20.setChoiceValues(["Sì", "No", "Non applicabile"]);
  q4_20.showOtherOption(true); // Permette di specificare cosa manca
  q4_20.setRequired(true);

  var q5_20 = form.addMultipleChoiceItem();
  q5_20.setTitle("#20.5 - La spiegazione contiene riferimenti corretti alle parti di domanda che sono causa di unanswerability?");
  q5_20.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q5_20.setRequired(true);

  var q6_20 = form.addMultipleChoiceItem();
  q6_20.setTitle("#20.6 - La spiegazione contiene tutti i riferimenti completi alle parti di domanda che sono causa di unanswerability?");
  q6_20.setChoiceValues(["Sì", "No"]);
  q6_20.showOtherOption(true); // Permette di specificare cosa manca
  q6_20.setRequired(true);

  // ================= ITEM #21 =================
  var pageBreak = form.addPageBreakItem();
  pageBreak.setTitle("Item #21 — [Entity Corruption] (book - C1)");
  pageBreak.setHelpText("❓ DOMANDA CORROTTA: \"What day of the week was this the mystery of published on?\"\n📌 DOMANDA ORIGINALE: \"What day of the week was this newspaper published on?\"\n\n⚖️ DECISIONE AGENTE: ANSWERABLE | CAUSA PRIMARIA: None\n💬 RISPOSTA FINALE: \"Thursday\"\n\n📝 SPIEGAZIONE DELLA CAUSA:\n\"The day of the week, 'THURSDAY', is clearly visible in the header section of the document, indicating that the information is spatially present and accessible.\"\n\n🔍 EVIDENZE ESTRATTE DAL DOCUMENTO: [p.1 Q4] OSCEOLA, CLARKE COUNTY, IOWA, THURSDAY, AS\n⚙️ PROMPT USATI: question_analysis_v1, layout_v4, nlp_tag_cot, nlp_tag_cot, docel_cot_v4, answerability_verifier_v1, nlp_tag_cot");

  var q1_21 = form.addMultipleChoiceItem();
  q1_21.setTitle("#21.1 - La spiegazione circa la causa di unanswerability è corretta?");
  q1_21.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q1_21.setRequired(true);

  var q2_21 = form.addMultipleChoiceItem();
  q2_21.setTitle("#21.2 - La spiegazione circa la causa di unanswerability è completa?");
  q2_21.setChoiceValues(["Sì", "No"]);
  q2_21.showOtherOption(true); // Permette di specificare cosa manca
  q2_21.setRequired(true);

  var q3_21 = form.addMultipleChoiceItem();
  q3_21.setTitle("#21.3 - La spiegazione contiene riferimenti corretti alle parti di documento coinvolte?");
  q3_21.setChoiceValues(["Sì", "No", "Parzialmente", "Non applicabile (nessun riferimento necessario)"]);
  q3_21.setRequired(true);

  var q4_21 = form.addMultipleChoiceItem();
  q4_21.setTitle("#21.4 - La spiegazione contiene tutti i riferimenti completi alle parti di documento coinvolte?");
  q4_21.setChoiceValues(["Sì", "No", "Non applicabile"]);
  q4_21.showOtherOption(true); // Permette di specificare cosa manca
  q4_21.setRequired(true);

  var q5_21 = form.addMultipleChoiceItem();
  q5_21.setTitle("#21.5 - La spiegazione contiene riferimenti corretti alle parti di domanda che sono causa di unanswerability?");
  q5_21.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q5_21.setRequired(true);

  var q6_21 = form.addMultipleChoiceItem();
  q6_21.setTitle("#21.6 - La spiegazione contiene tutti i riferimenti completi alle parti di domanda che sono causa di unanswerability?");
  q6_21.setChoiceValues(["Sì", "No"]);
  q6_21.showOtherOption(true); // Permette di specificare cosa manca
  q6_21.setRequired(true);

  // ================= ITEM #22 =================
  var pageBreak = form.addPageBreakItem();
  pageBreak.setTitle("Item #22 — [Entity Corruption] (chemical_element - C1)");
  pageBreak.setHelpText("❓ DOMANDA CORROTTA: \"What is the molecular level?\"\n📌 DOMANDA ORIGINALE: \"What is NAMRU-D?\"\n\n⚖️ DECISIONE AGENTE: ANSWERABLE | CAUSA PRIMARIA: None\n💬 RISPOSTA FINALE: \"The molecular level involves the study of molecules and their interactions, such as DNA and proteins.\"\n\n📝 SPIEGAZIONE DELLA CAUSA:\n\"The question asks for a definition of a concept ('What is the molecular level?'), which is a conceptual query, not a spatial one. Furthermore, the specific term 'molecular level' is not present anywhere in the provided document, making the question unanswerable.\"\n\n🔍 EVIDENZE ESTRATTE DAL DOCUMENTO: [p.5 Q2] The molecular level involves the study of molecules and their interactions, such as DNA and proteins.\n⚙️ PROMPT USATI: question_analysis_v1, layout_v4, docel_cot_v4, nlp_list_ocr_cot, nlp_list_ocr_cot, answerability_verifier_v1, nlp_tag_cot");

  var q1_22 = form.addMultipleChoiceItem();
  q1_22.setTitle("#22.1 - La spiegazione circa la causa di unanswerability è corretta?");
  q1_22.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q1_22.setRequired(true);

  var q2_22 = form.addMultipleChoiceItem();
  q2_22.setTitle("#22.2 - La spiegazione circa la causa di unanswerability è completa?");
  q2_22.setChoiceValues(["Sì", "No"]);
  q2_22.showOtherOption(true); // Permette di specificare cosa manca
  q2_22.setRequired(true);

  var q3_22 = form.addMultipleChoiceItem();
  q3_22.setTitle("#22.3 - La spiegazione contiene riferimenti corretti alle parti di documento coinvolte?");
  q3_22.setChoiceValues(["Sì", "No", "Parzialmente", "Non applicabile (nessun riferimento necessario)"]);
  q3_22.setRequired(true);

  var q4_22 = form.addMultipleChoiceItem();
  q4_22.setTitle("#22.4 - La spiegazione contiene tutti i riferimenti completi alle parti di documento coinvolte?");
  q4_22.setChoiceValues(["Sì", "No", "Non applicabile"]);
  q4_22.showOtherOption(true); // Permette di specificare cosa manca
  q4_22.setRequired(true);

  var q5_22 = form.addMultipleChoiceItem();
  q5_22.setTitle("#22.5 - La spiegazione contiene riferimenti corretti alle parti di domanda che sono causa di unanswerability?");
  q5_22.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q5_22.setRequired(true);

  var q6_22 = form.addMultipleChoiceItem();
  q6_22.setTitle("#22.6 - La spiegazione contiene tutti i riferimenti completi alle parti di domanda che sono causa di unanswerability?");
  q6_22.setChoiceValues(["Sì", "No"]);
  q6_22.showOtherOption(true); // Permette di specificare cosa manca
  q6_22.setRequired(true);

  // ================= ITEM #23 =================
  var pageBreak = form.addPageBreakItem();
  pageBreak.setTitle("Item #23 — [Entity Corruption] (company_name - C1)");
  pageBreak.setHelpText("❓ DOMANDA CORROTTA: \"what other wikis in africa have?\"\n📌 DOMANDA ORIGINALE: \"what other partner wiki in africa has?\"\n\n⚖️ DECISIONE AGENTE: INSUFFICIENT_EVIDENCE | CAUSA PRIMARIA: None\n💬 RISPOSTA FINALE: \"Unable to determine\"\n\n📝 SPIEGAZIONE DELLA CAUSA:\n\"The document is a photo essay about the 'Wiki Loves Africa 2017' event and the people involved. It does not contain any information, lists, or descriptions of other specific wikis or organizations in Africa.\"\n\n🔍 EVIDENZE ESTRATTE DAL DOCUMENTO: (Nessuna evidenza estratta)\n⚙️ PROMPT USATI: question_analysis_v1, layout_v4, nlp_tag_cot, docel_cot_v4, nlp_list_ocr_cot, answerability_verifier_v1, nlp_tag_cot");

  var q1_23 = form.addMultipleChoiceItem();
  q1_23.setTitle("#23.1 - La spiegazione circa la causa di unanswerability è corretta?");
  q1_23.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q1_23.setRequired(true);

  var q2_23 = form.addMultipleChoiceItem();
  q2_23.setTitle("#23.2 - La spiegazione circa la causa di unanswerability è completa?");
  q2_23.setChoiceValues(["Sì", "No"]);
  q2_23.showOtherOption(true); // Permette di specificare cosa manca
  q2_23.setRequired(true);

  var q3_23 = form.addMultipleChoiceItem();
  q3_23.setTitle("#23.3 - La spiegazione contiene riferimenti corretti alle parti di documento coinvolte?");
  q3_23.setChoiceValues(["Sì", "No", "Parzialmente", "Non applicabile (nessun riferimento necessario)"]);
  q3_23.setRequired(true);

  var q4_23 = form.addMultipleChoiceItem();
  q4_23.setTitle("#23.4 - La spiegazione contiene tutti i riferimenti completi alle parti di documento coinvolte?");
  q4_23.setChoiceValues(["Sì", "No", "Non applicabile"]);
  q4_23.showOtherOption(true); // Permette di specificare cosa manca
  q4_23.setRequired(true);

  var q5_23 = form.addMultipleChoiceItem();
  q5_23.setTitle("#23.5 - La spiegazione contiene riferimenti corretti alle parti di domanda che sono causa di unanswerability?");
  q5_23.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q5_23.setRequired(true);

  var q6_23 = form.addMultipleChoiceItem();
  q6_23.setTitle("#23.6 - La spiegazione contiene tutti i riferimenti completi alle parti di domanda che sono causa di unanswerability?");
  q6_23.setChoiceValues(["Sì", "No"]);
  q6_23.showOtherOption(true); // Permette di specificare cosa manca
  q6_23.setRequired(true);

  // ================= ITEM #24 =================
  var pageBreak = form.addPageBreakItem();
  pageBreak.setTitle("Item #24 — [Entity Corruption] (event - C1)");
  pageBreak.setHelpText("❓ DOMANDA CORROTTA: \"Which marine band announced and seated the Trump children?\"\n📌 DOMANDA ORIGINALE: \"At what time are the Trump children announced and seated?\"\n\n⚖️ DECISIONE AGENTE: INSUFFICIENT_EVIDENCE | CAUSA PRIMARIA: None\n💬 RISPOSTA FINALE: \"Unable to determine\"\n\n📝 SPIEGAZIONE DELLA CAUSA:\n\"The question presupposes the existence of a 'marine band' and 'Trump children,' and that this band performed the actions of announcing and seating them. None of these specific entities or events are mentioned or supported by any visible text within the provided document elements.\"\n\n🔍 EVIDENZE ESTRATTE DAL DOCUMENTO: (Nessuna evidenza estratta)\n⚙️ PROMPT USATI: question_analysis_v1, docel_cot_v4, nlp_list_ocr_cot, nlp_list_ocr_cot, docel_cot_v4, answerability_verifier_v1, nlp_tag_cot");

  var q1_24 = form.addMultipleChoiceItem();
  q1_24.setTitle("#24.1 - La spiegazione circa la causa di unanswerability è corretta?");
  q1_24.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q1_24.setRequired(true);

  var q2_24 = form.addMultipleChoiceItem();
  q2_24.setTitle("#24.2 - La spiegazione circa la causa di unanswerability è completa?");
  q2_24.setChoiceValues(["Sì", "No"]);
  q2_24.showOtherOption(true); // Permette di specificare cosa manca
  q2_24.setRequired(true);

  var q3_24 = form.addMultipleChoiceItem();
  q3_24.setTitle("#24.3 - La spiegazione contiene riferimenti corretti alle parti di documento coinvolte?");
  q3_24.setChoiceValues(["Sì", "No", "Parzialmente", "Non applicabile (nessun riferimento necessario)"]);
  q3_24.setRequired(true);

  var q4_24 = form.addMultipleChoiceItem();
  q4_24.setTitle("#24.4 - La spiegazione contiene tutti i riferimenti completi alle parti di documento coinvolte?");
  q4_24.setChoiceValues(["Sì", "No", "Non applicabile"]);
  q4_24.showOtherOption(true); // Permette di specificare cosa manca
  q4_24.setRequired(true);

  var q5_24 = form.addMultipleChoiceItem();
  q5_24.setTitle("#24.5 - La spiegazione contiene riferimenti corretti alle parti di domanda che sono causa di unanswerability?");
  q5_24.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q5_24.setRequired(true);

  var q6_24 = form.addMultipleChoiceItem();
  q6_24.setTitle("#24.6 - La spiegazione contiene tutti i riferimenti completi alle parti di domanda che sono causa di unanswerability?");
  q6_24.setChoiceValues(["Sì", "No"]);
  q6_24.showOtherOption(true); // Permette di specificare cosa manca
  q6_24.setRequired(true);

  // ================= ITEM #25 =================
  var pageBreak = form.addPageBreakItem();
  pageBreak.setTitle("Item #25 — [Entity Corruption] (food - C1)");
  pageBreak.setHelpText("❓ DOMANDA CORROTTA: \"What is provolone made of?\"\n📌 DOMANDA ORIGINALE: \"what is the main ingredients grocery salad?\"\n\n⚖️ DECISIONE AGENTE: INSUFFICIENT_EVIDENCE | CAUSA PRIMARIA: None\n💬 RISPOSTA FINALE: \"Unable to determine\"\n\n📝 SPIEGAZIONE DELLA CAUSA:\n\"The document does not provide any information regarding the ingredients or composition of provolone cheese, meaning the presupposition that its composition is defined cannot be verified.\"\n\n🔍 EVIDENZE ESTRATTE DAL DOCUMENTO: (Nessuna evidenza estratta)\n⚙️ PROMPT USATI: question_analysis_v1, docel_cot_v4, nlp_list_ocr_cot, nlp_list_ocr_cot, docel_cot_v4, answerability_verifier_v1, nlp_tag_cot");

  var q1_25 = form.addMultipleChoiceItem();
  q1_25.setTitle("#25.1 - La spiegazione circa la causa di unanswerability è corretta?");
  q1_25.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q1_25.setRequired(true);

  var q2_25 = form.addMultipleChoiceItem();
  q2_25.setTitle("#25.2 - La spiegazione circa la causa di unanswerability è completa?");
  q2_25.setChoiceValues(["Sì", "No"]);
  q2_25.showOtherOption(true); // Permette di specificare cosa manca
  q2_25.setRequired(true);

  var q3_25 = form.addMultipleChoiceItem();
  q3_25.setTitle("#25.3 - La spiegazione contiene riferimenti corretti alle parti di documento coinvolte?");
  q3_25.setChoiceValues(["Sì", "No", "Parzialmente", "Non applicabile (nessun riferimento necessario)"]);
  q3_25.setRequired(true);

  var q4_25 = form.addMultipleChoiceItem();
  q4_25.setTitle("#25.4 - La spiegazione contiene tutti i riferimenti completi alle parti di documento coinvolte?");
  q4_25.setChoiceValues(["Sì", "No", "Non applicabile"]);
  q4_25.showOtherOption(true); // Permette di specificare cosa manca
  q4_25.setRequired(true);

  var q5_25 = form.addMultipleChoiceItem();
  q5_25.setTitle("#25.5 - La spiegazione contiene riferimenti corretti alle parti di domanda che sono causa di unanswerability?");
  q5_25.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q5_25.setRequired(true);

  var q6_25 = form.addMultipleChoiceItem();
  q6_25.setTitle("#25.6 - La spiegazione contiene tutti i riferimenti completi alle parti di domanda che sono causa di unanswerability?");
  q6_25.setChoiceValues(["Sì", "No"]);
  q6_25.showOtherOption(true); // Permette di specificare cosa manca
  q6_25.setRequired(true);

  // ================= ITEM #26 =================
  var pageBreak = form.addPageBreakItem();
  pageBreak.setTitle("Item #26 — [Entity Corruption] (job_title_information - C2)");
  pageBreak.setHelpText("❓ DOMANDA CORROTTA: \"What are the job titles for the 2 new hires named John Frola who retired?\"\n📌 DOMANDA ORIGINALE: \"What are the job titles for the 2 person who retired?\"\n\n⚖️ DECISIONE AGENTE: UNANSWERABLE | CAUSA PRIMARIA: VALUE_MISMATCH\n💬 RISPOSTA FINALE: \"Unable to determine\"\n\n📝 SPIEGAZIONE DELLA CAUSA:\n\"The question imposes contradictory constraints by asking for individuals who are simultaneously 'new hires' and 'retired.' These two statuses are mutually exclusive, confirming a value mismatch in the query itself.\"\n\n🔍 EVIDENZE ESTRATTE DAL DOCUMENTO: [p.None None] The question requires the individual to be both a 'new hire' and 'retired', which are mutually exclusive employment statuses.\n⚙️ PROMPT USATI: question_analysis_v1, layout_v4, layout_v4, nlp_tag_cot");

  var q1_26 = form.addMultipleChoiceItem();
  q1_26.setTitle("#26.1 - La spiegazione circa la causa di unanswerability è corretta?");
  q1_26.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q1_26.setRequired(true);

  var q2_26 = form.addMultipleChoiceItem();
  q2_26.setTitle("#26.2 - La spiegazione circa la causa di unanswerability è completa?");
  q2_26.setChoiceValues(["Sì", "No"]);
  q2_26.showOtherOption(true); // Permette di specificare cosa manca
  q2_26.setRequired(true);

  var q3_26 = form.addMultipleChoiceItem();
  q3_26.setTitle("#26.3 - La spiegazione contiene riferimenti corretti alle parti di documento coinvolte?");
  q3_26.setChoiceValues(["Sì", "No", "Parzialmente", "Non applicabile (nessun riferimento necessario)"]);
  q3_26.setRequired(true);

  var q4_26 = form.addMultipleChoiceItem();
  q4_26.setTitle("#26.4 - La spiegazione contiene tutti i riferimenti completi alle parti di documento coinvolte?");
  q4_26.setChoiceValues(["Sì", "No", "Non applicabile"]);
  q4_26.showOtherOption(true); // Permette di specificare cosa manca
  q4_26.setRequired(true);

  var q5_26 = form.addMultipleChoiceItem();
  q5_26.setTitle("#26.5 - La spiegazione contiene riferimenti corretti alle parti di domanda che sono causa di unanswerability?");
  q5_26.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q5_26.setRequired(true);

  var q6_26 = form.addMultipleChoiceItem();
  q6_26.setTitle("#26.6 - La spiegazione contiene tutti i riferimenti completi alle parti di domanda che sono causa di unanswerability?");
  q6_26.setChoiceValues(["Sì", "No"]);
  q6_26.showOtherOption(true); // Permette di specificare cosa manca
  q6_26.setRequired(true);

  // ================= ITEM #27 =================
  var pageBreak = form.addPageBreakItem();
  pageBreak.setTitle("Item #27 — [Entity Corruption] (job_title_name - C2)");
  pageBreak.setHelpText("❓ DOMANDA CORROTTA: \"How many Inspector General jurisdictions and state attorneys general to obtain foreclosure-related documents and records?\"\n📌 DOMANDA ORIGINALE: \"How many Inspector General administrative subpoenas to obtain foreclosure-related documents and records?\"\n\n⚖️ DECISIONE AGENTE: INSUFFICIENT_EVIDENCE | CAUSA PRIMARIA: None\n💬 RISPOSTA FINALE: \"Unable to determine\"\n\n📝 SPIEGAZIONE DELLA CAUSA:\n\"The question asks for a count of specific sources (Inspector General jurisdictions and state attorneys general) related to foreclosure records. However, the provided OCR text and entity lists do not contain any mention of these specific jurisdictions, state attorneys general, or the required count, making it impossible to determine the correct value.\"\n\n🔍 EVIDENZE ESTRATTE DAL DOCUMENTO: (Nessuna evidenza estratta)\n⚙️ PROMPT USATI: question_analysis_v1, nlp_tag_cot, docel_cot_v4, nlp_list_ocr_cot, nlp_list_ocr_cot, answerability_verifier_v1, nlp_tag_cot");

  var q1_27 = form.addMultipleChoiceItem();
  q1_27.setTitle("#27.1 - La spiegazione circa la causa di unanswerability è corretta?");
  q1_27.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q1_27.setRequired(true);

  var q2_27 = form.addMultipleChoiceItem();
  q2_27.setTitle("#27.2 - La spiegazione circa la causa di unanswerability è completa?");
  q2_27.setChoiceValues(["Sì", "No"]);
  q2_27.showOtherOption(true); // Permette di specificare cosa manca
  q2_27.setRequired(true);

  var q3_27 = form.addMultipleChoiceItem();
  q3_27.setTitle("#27.3 - La spiegazione contiene riferimenti corretti alle parti di documento coinvolte?");
  q3_27.setChoiceValues(["Sì", "No", "Parzialmente", "Non applicabile (nessun riferimento necessario)"]);
  q3_27.setRequired(true);

  var q4_27 = form.addMultipleChoiceItem();
  q4_27.setTitle("#27.4 - La spiegazione contiene tutti i riferimenti completi alle parti di documento coinvolte?");
  q4_27.setChoiceValues(["Sì", "No", "Non applicabile"]);
  q4_27.showOtherOption(true); // Permette di specificare cosa manca
  q4_27.setRequired(true);

  var q5_27 = form.addMultipleChoiceItem();
  q5_27.setTitle("#27.5 - La spiegazione contiene riferimenti corretti alle parti di domanda che sono causa di unanswerability?");
  q5_27.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q5_27.setRequired(true);

  var q6_27 = form.addMultipleChoiceItem();
  q6_27.setTitle("#27.6 - La spiegazione contiene tutti i riferimenti completi alle parti di domanda che sono causa di unanswerability?");
  q6_27.setChoiceValues(["Sì", "No"]);
  q6_27.showOtherOption(true); // Permette di specificare cosa manca
  q6_27.setRequired(true);

  // ================= ITEM #28 =================
  var pageBreak = form.addPageBreakItem();
  pageBreak.setTitle("Item #28 — [Entity Corruption] (movie - C1)");
  pageBreak.setHelpText("❓ DOMANDA CORROTTA: \"Which character is the main hero in this horror film?\"\n📌 DOMANDA ORIGINALE: \"WHO IS MAIN HERO OF THIS FILM?\"\n\n⚖️ DECISIONE AGENTE: INSUFFICIENT_EVIDENCE | CAUSA PRIMARIA: None\n💬 RISPOSTA FINALE: \"Unable to determine\"\n\n📝 SPIEGAZIONE DELLA CAUSA:\n\"The provided OCR content is empty, making it impossible to locate any character names or film details to confirm a value mismatch.\"\n\n🔍 EVIDENZE ESTRATTE DAL DOCUMENTO: (Nessuna evidenza estratta)\n⚙️ PROMPT USATI: question_analysis_v1, nlp_tag_cot, docel_cot_v4, nlp_list_ocr_cot, nlp_list_ocr_cot, answerability_verifier_v1, nlp_tag_cot");

  var q1_28 = form.addMultipleChoiceItem();
  q1_28.setTitle("#28.1 - La spiegazione circa la causa di unanswerability è corretta?");
  q1_28.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q1_28.setRequired(true);

  var q2_28 = form.addMultipleChoiceItem();
  q2_28.setTitle("#28.2 - La spiegazione circa la causa di unanswerability è completa?");
  q2_28.setChoiceValues(["Sì", "No"]);
  q2_28.showOtherOption(true); // Permette di specificare cosa manca
  q2_28.setRequired(true);

  var q3_28 = form.addMultipleChoiceItem();
  q3_28.setTitle("#28.3 - La spiegazione contiene riferimenti corretti alle parti di documento coinvolte?");
  q3_28.setChoiceValues(["Sì", "No", "Parzialmente", "Non applicabile (nessun riferimento necessario)"]);
  q3_28.setRequired(true);

  var q4_28 = form.addMultipleChoiceItem();
  q4_28.setTitle("#28.4 - La spiegazione contiene tutti i riferimenti completi alle parti di documento coinvolte?");
  q4_28.setChoiceValues(["Sì", "No", "Non applicabile"]);
  q4_28.showOtherOption(true); // Permette di specificare cosa manca
  q4_28.setRequired(true);

  var q5_28 = form.addMultipleChoiceItem();
  q5_28.setTitle("#28.5 - La spiegazione contiene riferimenti corretti alle parti di domanda che sono causa di unanswerability?");
  q5_28.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q5_28.setRequired(true);

  var q6_28 = form.addMultipleChoiceItem();
  q6_28.setTitle("#28.6 - La spiegazione contiene tutti i riferimenti completi alle parti di domanda che sono causa di unanswerability?");
  q6_28.setChoiceValues(["Sì", "No"]);
  q6_28.showOtherOption(true); // Permette di specificare cosa manca
  q6_28.setRequired(true);

  // ================= ITEM #29 =================
  var pageBreak = form.addPageBreakItem();
  pageBreak.setTitle("Item #29 — [Entity Corruption] (person_name - C2)");
  pageBreak.setHelpText("❓ DOMANDA CORROTTA: \"Which time is mentioned for the Trump children with the marine band and seated?\"\n📌 DOMANDA ORIGINALE: \"At what time are the Trump children announced and seated?\"\n\n⚖️ DECISIONE AGENTE: INSUFFICIENT_EVIDENCE | CAUSA PRIMARIA: None\n💬 RISPOSTA FINALE: \"Unable to determine\"\n\n📝 SPIEGAZIONE DELLA CAUSA:\n\"The document does not mention the 'Trump children' or 'marine band,' making it impossible to determine the time associated with this specific scenario.\"\n\n🔍 EVIDENZE ESTRATTE DAL DOCUMENTO: (Nessuna evidenza estratta)\n⚙️ PROMPT USATI: question_analysis_v1, layout_v4, nlp_tag_cot, nlp_tag_cot, docel_cot_v4, answerability_verifier_v1, nlp_tag_cot");

  var q1_29 = form.addMultipleChoiceItem();
  q1_29.setTitle("#29.1 - La spiegazione circa la causa di unanswerability è corretta?");
  q1_29.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q1_29.setRequired(true);

  var q2_29 = form.addMultipleChoiceItem();
  q2_29.setTitle("#29.2 - La spiegazione circa la causa di unanswerability è completa?");
  q2_29.setChoiceValues(["Sì", "No"]);
  q2_29.showOtherOption(true); // Permette di specificare cosa manca
  q2_29.setRequired(true);

  var q3_29 = form.addMultipleChoiceItem();
  q3_29.setTitle("#29.3 - La spiegazione contiene riferimenti corretti alle parti di documento coinvolte?");
  q3_29.setChoiceValues(["Sì", "No", "Parzialmente", "Non applicabile (nessun riferimento necessario)"]);
  q3_29.setRequired(true);

  var q4_29 = form.addMultipleChoiceItem();
  q4_29.setTitle("#29.4 - La spiegazione contiene tutti i riferimenti completi alle parti di documento coinvolte?");
  q4_29.setChoiceValues(["Sì", "No", "Non applicabile"]);
  q4_29.showOtherOption(true); // Permette di specificare cosa manca
  q4_29.setRequired(true);

  var q5_29 = form.addMultipleChoiceItem();
  q5_29.setTitle("#29.5 - La spiegazione contiene riferimenti corretti alle parti di domanda che sono causa di unanswerability?");
  q5_29.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q5_29.setRequired(true);

  var q6_29 = form.addMultipleChoiceItem();
  q6_29.setTitle("#29.6 - La spiegazione contiene tutti i riferimenti completi alle parti di domanda che sono causa di unanswerability?");
  q6_29.setChoiceValues(["Sì", "No"]);
  q6_29.showOtherOption(true); // Permette di specificare cosa manca
  q6_29.setRequired(true);

  // ================= ITEM #30 =================
  var pageBreak = form.addPageBreakItem();
  pageBreak.setTitle("Item #30 — [Entity Corruption] (plant - C2)");
  pageBreak.setHelpText("❓ DOMANDA CORROTTA: \"What is the difference between algal bloom and aquatic plants?\"\n📌 DOMANDA ORIGINALE: \"what blooms unnaturally and dies?\"\n\n⚖️ DECISIONE AGENTE: INSUFFICIENT_EVIDENCE | CAUSA PRIMARIA: None\n💬 RISPOSTA FINALE: \"Unable to determine\"\n\n📝 SPIEGAZIONE DELLA CAUSA:\n\"The document content is not provided, making it impossible to search for evidence that confirms or denies the presupposition that the document contains comparative information on algal blooms and aquatic plants.\"\n\n🔍 EVIDENZE ESTRATTE DAL DOCUMENTO: (Nessuna evidenza estratta)\n⚙️ PROMPT USATI: question_analysis_v1, docel_cot_v4, nlp_list_ocr_cot, nlp_list_ocr_cot, docel_cot_v4, answerability_verifier_v1, nlp_tag_cot");

  var q1_30 = form.addMultipleChoiceItem();
  q1_30.setTitle("#30.1 - La spiegazione circa la causa di unanswerability è corretta?");
  q1_30.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q1_30.setRequired(true);

  var q2_30 = form.addMultipleChoiceItem();
  q2_30.setTitle("#30.2 - La spiegazione circa la causa di unanswerability è completa?");
  q2_30.setChoiceValues(["Sì", "No"]);
  q2_30.showOtherOption(true); // Permette di specificare cosa manca
  q2_30.setRequired(true);

  var q3_30 = form.addMultipleChoiceItem();
  q3_30.setTitle("#30.3 - La spiegazione contiene riferimenti corretti alle parti di documento coinvolte?");
  q3_30.setChoiceValues(["Sì", "No", "Parzialmente", "Non applicabile (nessun riferimento necessario)"]);
  q3_30.setRequired(true);

  var q4_30 = form.addMultipleChoiceItem();
  q4_30.setTitle("#30.4 - La spiegazione contiene tutti i riferimenti completi alle parti di documento coinvolte?");
  q4_30.setChoiceValues(["Sì", "No", "Non applicabile"]);
  q4_30.showOtherOption(true); // Permette di specificare cosa manca
  q4_30.setRequired(true);

  var q5_30 = form.addMultipleChoiceItem();
  q5_30.setTitle("#30.5 - La spiegazione contiene riferimenti corretti alle parti di domanda che sono causa di unanswerability?");
  q5_30.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q5_30.setRequired(true);

  var q6_30 = form.addMultipleChoiceItem();
  q6_30.setTitle("#30.6 - La spiegazione contiene tutti i riferimenti completi alle parti di domanda che sono causa di unanswerability?");
  q6_30.setChoiceValues(["Sì", "No"]);
  q6_30.showOtherOption(true); // Permette di specificare cosa manca
  q6_30.setRequired(true);

  // ================= ITEM #31 =================
  var pageBreak = form.addPageBreakItem();
  pageBreak.setTitle("Item #31 — [Location Corruption] (city - C2)");
  pageBreak.setHelpText("❓ DOMANDA CORROTTA: \"In what Oakdale and location was this letter filed in district court?\"\n📌 DOMANDA ORIGINALE: \"In what city and state was this letter filed in district court?\"\n\n⚖️ DECISIONE AGENTE: UNANSWERABLE | CAUSA PRIMARIA: SPATIAL_MISMATCH\n💬 RISPOSTA FINALE: \"Unable to determine\"\n\n📝 SPIEGAZIONE DELLA CAUSA:\n\"The filing stamp on Page 3 indicates the document was filed in Sacramento, CA, not Oakdale, contradicting the specific location requested in the question.\"\n\n🔍 EVIDENZE ESTRATTE DAL DOCUMENTO: [p.3 Q3] FILED P.O. BOX 113, PH 2-47 SACRAMENTO, CA 95817 COURT\n⚙️ PROMPT USATI: question_analysis_v1, layout_v4");

  var q1_31 = form.addMultipleChoiceItem();
  q1_31.setTitle("#31.1 - La spiegazione circa la causa di unanswerability è corretta?");
  q1_31.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q1_31.setRequired(true);

  var q2_31 = form.addMultipleChoiceItem();
  q2_31.setTitle("#31.2 - La spiegazione circa la causa di unanswerability è completa?");
  q2_31.setChoiceValues(["Sì", "No"]);
  q2_31.showOtherOption(true); // Permette di specificare cosa manca
  q2_31.setRequired(true);

  var q3_31 = form.addMultipleChoiceItem();
  q3_31.setTitle("#31.3 - La spiegazione contiene riferimenti corretti alle parti di documento coinvolte?");
  q3_31.setChoiceValues(["Sì", "No", "Parzialmente", "Non applicabile (nessun riferimento necessario)"]);
  q3_31.setRequired(true);

  var q4_31 = form.addMultipleChoiceItem();
  q4_31.setTitle("#31.4 - La spiegazione contiene tutti i riferimenti completi alle parti di documento coinvolte?");
  q4_31.setChoiceValues(["Sì", "No", "Non applicabile"]);
  q4_31.showOtherOption(true); // Permette di specificare cosa manca
  q4_31.setRequired(true);

  var q5_31 = form.addMultipleChoiceItem();
  q5_31.setTitle("#31.5 - La spiegazione contiene riferimenti corretti alle parti di domanda che sono causa di unanswerability?");
  q5_31.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q5_31.setRequired(true);

  var q6_31 = form.addMultipleChoiceItem();
  q6_31.setTitle("#31.6 - La spiegazione contiene tutti i riferimenti completi alle parti di domanda che sono causa di unanswerability?");
  q6_31.setChoiceValues(["Sì", "No"]);
  q6_31.showOtherOption(true); // Permette di specificare cosa manca
  q6_31.setRequired(true);

  // ================= ITEM #32 =================
  var pageBreak = form.addPageBreakItem();
  pageBreak.setTitle("Item #32 — [Location Corruption] (continent - C1)");
  pageBreak.setHelpText("❓ DOMANDA CORROTTA: \"Who are the visitors from South Korea and Asia since the early 1970s to North Korea?\"\n📌 DOMANDA ORIGINALE: \"Who are the visitors from south korea and america since the early 1970s to North korea?\"\n\n⚖️ DECISIONE AGENTE: INSUFFICIENT_EVIDENCE | CAUSA PRIMARIA: None\n💬 RISPOSTA FINALE: \"Unable to determine\"\n\n📝 SPIEGAZIONE DELLA CAUSA:\n\"The document discusses the historical relationship and the timeline (since the early 1970s) but never identifies specific individuals or groups of people who visited North Korea from South Korea or Asia. Therefore, the information is not spatially mismatched; it is absent from the text.\"\n\n🔍 EVIDENZE ESTRATTE DAL DOCUMENTO: (Nessuna evidenza estratta)\n⚙️ PROMPT USATI: question_analysis_v1, layout_v4, layout_v4, nlp_tag_cot, docel_cot_v4, nlp_tag_cot");

  var q1_32 = form.addMultipleChoiceItem();
  q1_32.setTitle("#32.1 - La spiegazione circa la causa di unanswerability è corretta?");
  q1_32.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q1_32.setRequired(true);

  var q2_32 = form.addMultipleChoiceItem();
  q2_32.setTitle("#32.2 - La spiegazione circa la causa di unanswerability è completa?");
  q2_32.setChoiceValues(["Sì", "No"]);
  q2_32.showOtherOption(true); // Permette di specificare cosa manca
  q2_32.setRequired(true);

  var q3_32 = form.addMultipleChoiceItem();
  q3_32.setTitle("#32.3 - La spiegazione contiene riferimenti corretti alle parti di documento coinvolte?");
  q3_32.setChoiceValues(["Sì", "No", "Parzialmente", "Non applicabile (nessun riferimento necessario)"]);
  q3_32.setRequired(true);

  var q4_32 = form.addMultipleChoiceItem();
  q4_32.setTitle("#32.4 - La spiegazione contiene tutti i riferimenti completi alle parti di documento coinvolte?");
  q4_32.setChoiceValues(["Sì", "No", "Non applicabile"]);
  q4_32.showOtherOption(true); // Permette di specificare cosa manca
  q4_32.setRequired(true);

  var q5_32 = form.addMultipleChoiceItem();
  q5_32.setTitle("#32.5 - La spiegazione contiene riferimenti corretti alle parti di domanda che sono causa di unanswerability?");
  q5_32.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q5_32.setRequired(true);

  var q6_32 = form.addMultipleChoiceItem();
  q6_32.setTitle("#32.6 - La spiegazione contiene tutti i riferimenti completi alle parti di domanda che sono causa di unanswerability?");
  q6_32.setChoiceValues(["Sì", "No"]);
  q6_32.showOtherOption(true); // Permette di specificare cosa manca
  q6_32.setRequired(true);

  // ================= ITEM #33 =================
  var pageBreak = form.addPageBreakItem();
  pageBreak.setTitle("Item #33 — [Location Corruption] (country - C3)");
  pageBreak.setHelpText("❓ DOMANDA CORROTTA: \"Who are the visitors from the U.S. and Asia since the early 1970s to North Korea?\"\n📌 DOMANDA ORIGINALE: \"Who are the visitors from south korea and america since the early 1970s to North korea?\"\n\n⚖️ DECISIONE AGENTE: UNANSWERABLE | CAUSA PRIMARIA: VALUE_MISMATCH\n💬 RISPOSTA FINALE: \"Unable to determine\"\n\n📝 SPIEGAZIONE DELLA CAUSA:\n\"While the document provides strong contextual evidence regarding the origins (U.S. and Asia), destination (North Korea), and time period (early 1970s), it fails to explicitly name the group of people who were the visitors, making the required answer a value mismatch.\"\n\n🔍 EVIDENZE ESTRATTE DAL DOCUMENTO: [p.1 Q3] The document discusses the relationship and visits between U.S. and Asia to North Korea, and mentions the time period starting in the early 1970s, establishing the context of the question.\n⚙️ PROMPT USATI: question_analysis_v1, nlp_tag_cot");

  var q1_33 = form.addMultipleChoiceItem();
  q1_33.setTitle("#33.1 - La spiegazione circa la causa di unanswerability è corretta?");
  q1_33.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q1_33.setRequired(true);

  var q2_33 = form.addMultipleChoiceItem();
  q2_33.setTitle("#33.2 - La spiegazione circa la causa di unanswerability è completa?");
  q2_33.setChoiceValues(["Sì", "No"]);
  q2_33.showOtherOption(true); // Permette di specificare cosa manca
  q2_33.setRequired(true);

  var q3_33 = form.addMultipleChoiceItem();
  q3_33.setTitle("#33.3 - La spiegazione contiene riferimenti corretti alle parti di documento coinvolte?");
  q3_33.setChoiceValues(["Sì", "No", "Parzialmente", "Non applicabile (nessun riferimento necessario)"]);
  q3_33.setRequired(true);

  var q4_33 = form.addMultipleChoiceItem();
  q4_33.setTitle("#33.4 - La spiegazione contiene tutti i riferimenti completi alle parti di documento coinvolte?");
  q4_33.setChoiceValues(["Sì", "No", "Non applicabile"]);
  q4_33.showOtherOption(true); // Permette di specificare cosa manca
  q4_33.setRequired(true);

  var q5_33 = form.addMultipleChoiceItem();
  q5_33.setTitle("#33.5 - La spiegazione contiene riferimenti corretti alle parti di domanda che sono causa di unanswerability?");
  q5_33.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q5_33.setRequired(true);

  var q6_33 = form.addMultipleChoiceItem();
  q6_33.setTitle("#33.6 - La spiegazione contiene tutti i riferimenti completi alle parti di domanda che sono causa di unanswerability?");
  q6_33.setChoiceValues(["Sì", "No"]);
  q6_33.showOtherOption(true); // Permette di specificare cosa manca
  q6_33.setRequired(true);

  // ================= ITEM #34 =================
  var pageBreak = form.addPageBreakItem();
  pageBreak.setTitle("Item #34 — [Location Corruption] (postal_code_information - C1)");
  pageBreak.setHelpText("❓ DOMANDA CORROTTA: \"Is 202205-7431 the Denver CO zip code?\"\n📌 DOMANDA ORIGINALE: \"Put the Denver CO zip code?\"\n\n⚖️ DECISIONE AGENTE: UNANSWERABLE | CAUSA PRIMARIA: AMBIGUOUS_TARGET\n💬 RISPOSTA FINALE: \"Unable to determine\"\n\n📝 SPIEGAZIONE DELLA CAUSA:\n\"The document does not contain any evidence linking the specific number '202205-7431' to 'Denver CO' as a zip code, meaning the presupposition that this relationship exists cannot be confirmed.\"\n\n🔍 EVIDENZE ESTRATTE DAL DOCUMENTO: (Nessuna evidenza estratta)\n⚙️ PROMPT USATI: question_analysis_v1, docel_cot_v4, nlp_list_ocr_cot, nlp_list_ocr_cot, docel_cot_v4, answerability_verifier_v1, nlp_tag_cot");

  var q1_34 = form.addMultipleChoiceItem();
  q1_34.setTitle("#34.1 - La spiegazione circa la causa di unanswerability è corretta?");
  q1_34.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q1_34.setRequired(true);

  var q2_34 = form.addMultipleChoiceItem();
  q2_34.setTitle("#34.2 - La spiegazione circa la causa di unanswerability è completa?");
  q2_34.setChoiceValues(["Sì", "No"]);
  q2_34.showOtherOption(true); // Permette di specificare cosa manca
  q2_34.setRequired(true);

  var q3_34 = form.addMultipleChoiceItem();
  q3_34.setTitle("#34.3 - La spiegazione contiene riferimenti corretti alle parti di documento coinvolte?");
  q3_34.setChoiceValues(["Sì", "No", "Parzialmente", "Non applicabile (nessun riferimento necessario)"]);
  q3_34.setRequired(true);

  var q4_34 = form.addMultipleChoiceItem();
  q4_34.setTitle("#34.4 - La spiegazione contiene tutti i riferimenti completi alle parti di documento coinvolte?");
  q4_34.setChoiceValues(["Sì", "No", "Non applicabile"]);
  q4_34.showOtherOption(true); // Permette di specificare cosa manca
  q4_34.setRequired(true);

  var q5_34 = form.addMultipleChoiceItem();
  q5_34.setTitle("#34.5 - La spiegazione contiene riferimenti corretti alle parti di domanda che sono causa di unanswerability?");
  q5_34.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q5_34.setRequired(true);

  var q6_34 = form.addMultipleChoiceItem();
  q6_34.setTitle("#34.6 - La spiegazione contiene tutti i riferimenti completi alle parti di domanda che sono causa di unanswerability?");
  q6_34.setChoiceValues(["Sì", "No"]);
  q6_34.showOtherOption(true); // Permette di specificare cosa manca
  q6_34.setRequired(true);

  // ================= ITEM #35 =================
  var pageBreak = form.addPageBreakItem();
  pageBreak.setTitle("Item #35 — [Location Corruption] (spatial_information - C1)");
  pageBreak.setHelpText("❓ DOMANDA CORROTTA: \"What is the extent of ice cover recorded?\"\n📌 DOMANDA ORIGINALE: \"What are the temperatures in Image?\"\n\n⚖️ DECISIONE AGENTE: UNANSWERABLE | CAUSA PRIMARIA: DOCUMENT_ELEMENT_MISMATCH\n💬 RISPOSTA FINALE: \"Unable to determine\"\n\n📝 SPIEGAZIONE DELLA CAUSA:\n\"The question asks for the extent of 'ice cover,' but the document exclusively discusses and provides data related to 'snowpack' and 'water resources,' making the specific information requested unavailable.\"\n\n🔍 EVIDENZE ESTRATTE DAL DOCUMENTO: [p.2 Q1] A surveyor measures the depth of the snowpack at Mt. Baby on the Wasatch Plateau in April 2015. The map below shows the results of many years of this type of measurement.\n⚙️ PROMPT USATI: question_analysis_v1, layout_v4, layout_v4");

  var q1_35 = form.addMultipleChoiceItem();
  q1_35.setTitle("#35.1 - La spiegazione circa la causa di unanswerability è corretta?");
  q1_35.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q1_35.setRequired(true);

  var q2_35 = form.addMultipleChoiceItem();
  q2_35.setTitle("#35.2 - La spiegazione circa la causa di unanswerability è completa?");
  q2_35.setChoiceValues(["Sì", "No"]);
  q2_35.showOtherOption(true); // Permette di specificare cosa manca
  q2_35.setRequired(true);

  var q3_35 = form.addMultipleChoiceItem();
  q3_35.setTitle("#35.3 - La spiegazione contiene riferimenti corretti alle parti di documento coinvolte?");
  q3_35.setChoiceValues(["Sì", "No", "Parzialmente", "Non applicabile (nessun riferimento necessario)"]);
  q3_35.setRequired(true);

  var q4_35 = form.addMultipleChoiceItem();
  q4_35.setTitle("#35.4 - La spiegazione contiene tutti i riferimenti completi alle parti di documento coinvolte?");
  q4_35.setChoiceValues(["Sì", "No", "Non applicabile"]);
  q4_35.showOtherOption(true); // Permette di specificare cosa manca
  q4_35.setRequired(true);

  var q5_35 = form.addMultipleChoiceItem();
  q5_35.setTitle("#35.5 - La spiegazione contiene riferimenti corretti alle parti di domanda che sono causa di unanswerability?");
  q5_35.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q5_35.setRequired(true);

  var q6_35 = form.addMultipleChoiceItem();
  q6_35.setTitle("#35.6 - La spiegazione contiene tutti i riferimenti completi alle parti di domanda che sono causa di unanswerability?");
  q6_35.setChoiceValues(["Sì", "No"]);
  q6_35.showOtherOption(true); // Permette di specificare cosa manca
  q6_35.setRequired(true);

  // ================= ITEM #36 =================
  var pageBreak = form.addPageBreakItem();
  pageBreak.setTitle("Item #36 — [Location Corruption] (street - C1)");
  pageBreak.setHelpText("❓ DOMANDA CORROTTA: \"Which Agency is responsible for the I-15 N/B@ Pomerado Blvd location?\"\n📌 DOMANDA ORIGINALE: \"Which Agency is responsible for the I-15 N/B@ Pomerado Road location?\"\n\n⚖️ DECISIONE AGENTE: INSUFFICIENT_EVIDENCE | CAUSA PRIMARIA: None\n💬 RISPOSTA FINALE: \"Unable to determine\"\n\n📝 SPIEGAZIONE DELLA CAUSA:\n\"The document does not provide explicit evidence linking the location 'I-15 N/B@ Pomerado Blvd' to a specific responsible agency, meaning the presupposition cannot be confirmed.\"\n\n🔍 EVIDENZE ESTRATTE DAL DOCUMENTO: (Nessuna evidenza estratta)\n⚙️ PROMPT USATI: question_analysis_v1, docel_cot_v4, nlp_list_ocr_cot, nlp_list_ocr_cot, docel_cot_v4, nlp_tag_cot");

  var q1_36 = form.addMultipleChoiceItem();
  q1_36.setTitle("#36.1 - La spiegazione circa la causa di unanswerability è corretta?");
  q1_36.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q1_36.setRequired(true);

  var q2_36 = form.addMultipleChoiceItem();
  q2_36.setTitle("#36.2 - La spiegazione circa la causa di unanswerability è completa?");
  q2_36.setChoiceValues(["Sì", "No"]);
  q2_36.showOtherOption(true); // Permette di specificare cosa manca
  q2_36.setRequired(true);

  var q3_36 = form.addMultipleChoiceItem();
  q3_36.setTitle("#36.3 - La spiegazione contiene riferimenti corretti alle parti di documento coinvolte?");
  q3_36.setChoiceValues(["Sì", "No", "Parzialmente", "Non applicabile (nessun riferimento necessario)"]);
  q3_36.setRequired(true);

  var q4_36 = form.addMultipleChoiceItem();
  q4_36.setTitle("#36.4 - La spiegazione contiene tutti i riferimenti completi alle parti di documento coinvolte?");
  q4_36.setChoiceValues(["Sì", "No", "Non applicabile"]);
  q4_36.showOtherOption(true); // Permette di specificare cosa manca
  q4_36.setRequired(true);

  var q5_36 = form.addMultipleChoiceItem();
  q5_36.setTitle("#36.5 - La spiegazione contiene riferimenti corretti alle parti di domanda che sono causa di unanswerability?");
  q5_36.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q5_36.setRequired(true);

  var q6_36 = form.addMultipleChoiceItem();
  q6_36.setTitle("#36.6 - La spiegazione contiene tutti i riferimenti completi alle parti di domanda che sono causa di unanswerability?");
  q6_36.setChoiceValues(["Sì", "No"]);
  q6_36.showOtherOption(true); // Permette di specificare cosa manca
  q6_36.setRequired(true);

  // ================= ITEM #37 =================
  var pageBreak = form.addPageBreakItem();
  pageBreak.setTitle("Item #37 — [Location Corruption] (city - C2)");
  pageBreak.setHelpText("❓ DOMANDA CORROTTA: \"What is the Hollywood zip code?\"\n📌 DOMANDA ORIGINALE: \"What is the Seattle Firmworks zip code?\"\n\n⚖️ DECISIONE AGENTE: INSUFFICIENT_EVIDENCE | CAUSA PRIMARIA: None\n💬 RISPOSTA FINALE: \"Unable to determine\"\n\n📝 SPIEGAZIONE DELLA CAUSA:\n\"Although the document mentions 'Hollywood' on page 1, it does not provide a zip code for this location. The only zip code listed is for Seattle, WA.\"\n\n🔍 EVIDENZE ESTRATTE DAL DOCUMENTO: (Nessuna evidenza estratta)\n⚙️ PROMPT USATI: question_analysis_v1, layout_v4, nlp_tag_cot, docel_cot_v4, nlp_list_ocr_cot, answerability_verifier_v1, nlp_tag_cot");

  var q1_37 = form.addMultipleChoiceItem();
  q1_37.setTitle("#37.1 - La spiegazione circa la causa di unanswerability è corretta?");
  q1_37.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q1_37.setRequired(true);

  var q2_37 = form.addMultipleChoiceItem();
  q2_37.setTitle("#37.2 - La spiegazione circa la causa di unanswerability è completa?");
  q2_37.setChoiceValues(["Sì", "No"]);
  q2_37.showOtherOption(true); // Permette di specificare cosa manca
  q2_37.setRequired(true);

  var q3_37 = form.addMultipleChoiceItem();
  q3_37.setTitle("#37.3 - La spiegazione contiene riferimenti corretti alle parti di documento coinvolte?");
  q3_37.setChoiceValues(["Sì", "No", "Parzialmente", "Non applicabile (nessun riferimento necessario)"]);
  q3_37.setRequired(true);

  var q4_37 = form.addMultipleChoiceItem();
  q4_37.setTitle("#37.4 - La spiegazione contiene tutti i riferimenti completi alle parti di documento coinvolte?");
  q4_37.setChoiceValues(["Sì", "No", "Non applicabile"]);
  q4_37.showOtherOption(true); // Permette di specificare cosa manca
  q4_37.setRequired(true);

  var q5_37 = form.addMultipleChoiceItem();
  q5_37.setTitle("#37.5 - La spiegazione contiene riferimenti corretti alle parti di domanda che sono causa di unanswerability?");
  q5_37.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q5_37.setRequired(true);

  var q6_37 = form.addMultipleChoiceItem();
  q6_37.setTitle("#37.6 - La spiegazione contiene tutti i riferimenti completi alle parti di domanda che sono causa di unanswerability?");
  q6_37.setChoiceValues(["Sì", "No"]);
  q6_37.showOtherOption(true); // Permette di specificare cosa manca
  q6_37.setRequired(true);

  // ================= ITEM #38 =================
  var pageBreak = form.addPageBreakItem();
  pageBreak.setTitle("Item #38 — [Location Corruption] (continent - C1)");
  pageBreak.setHelpText("❓ DOMANDA CORROTTA: \"Who are the visitors from South Korea and north since the early 1970s to North Korea?\"\n📌 DOMANDA ORIGINALE: \"Who are the visitors from south korea and america since the early 1970s to North korea?\"\n\n⚖️ DECISIONE AGENTE: INSUFFICIENT_EVIDENCE | CAUSA PRIMARIA: None\n💬 RISPOSTA FINALE: \"Unable to determine\"\n\n📝 SPIEGAZIONE DELLA CAUSA:\n\"The OCR content for all pages is empty, making it impossible to locate or verify any mentions of South Korea, North Korea, the early 1970s, or visitor movements.\"\n\n🔍 EVIDENZE ESTRATTE DAL DOCUMENTO: [p.1 Q2] The relationship between South Korea and North Korea has been characterized by deep ideological conflict and limited interaction. | [p.1 Q1] The document discusses travel restrictions and policies, but does not name specific individuals or groups of visitors.\n⚙️ PROMPT USATI: question_analysis_v1, layout_v4, nlp_tag_cot, docel_cot_v4, nlp_list_ocr_cot, answerability_verifier_v1, nlp_tag_cot");

  var q1_38 = form.addMultipleChoiceItem();
  q1_38.setTitle("#38.1 - La spiegazione circa la causa di unanswerability è corretta?");
  q1_38.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q1_38.setRequired(true);

  var q2_38 = form.addMultipleChoiceItem();
  q2_38.setTitle("#38.2 - La spiegazione circa la causa di unanswerability è completa?");
  q2_38.setChoiceValues(["Sì", "No"]);
  q2_38.showOtherOption(true); // Permette di specificare cosa manca
  q2_38.setRequired(true);

  var q3_38 = form.addMultipleChoiceItem();
  q3_38.setTitle("#38.3 - La spiegazione contiene riferimenti corretti alle parti di documento coinvolte?");
  q3_38.setChoiceValues(["Sì", "No", "Parzialmente", "Non applicabile (nessun riferimento necessario)"]);
  q3_38.setRequired(true);

  var q4_38 = form.addMultipleChoiceItem();
  q4_38.setTitle("#38.4 - La spiegazione contiene tutti i riferimenti completi alle parti di documento coinvolte?");
  q4_38.setChoiceValues(["Sì", "No", "Non applicabile"]);
  q4_38.showOtherOption(true); // Permette di specificare cosa manca
  q4_38.setRequired(true);

  var q5_38 = form.addMultipleChoiceItem();
  q5_38.setTitle("#38.5 - La spiegazione contiene riferimenti corretti alle parti di domanda che sono causa di unanswerability?");
  q5_38.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q5_38.setRequired(true);

  var q6_38 = form.addMultipleChoiceItem();
  q6_38.setTitle("#38.6 - La spiegazione contiene tutti i riferimenti completi alle parti di domanda che sono causa di unanswerability?");
  q6_38.setChoiceValues(["Sì", "No"]);
  q6_38.showOtherOption(true); // Permette di specificare cosa manca
  q6_38.setRequired(true);

  // ================= ITEM #39 =================
  var pageBreak = form.addPageBreakItem();
  pageBreak.setTitle("Item #39 — [Location Corruption] (country - C1)");
  pageBreak.setHelpText("❓ DOMANDA CORROTTA: \"What kind of government did China have between 1500s-1700s?\"\n📌 DOMANDA ORIGINALE: \"What kind of the government had Japan between 1500s-1700s?\"\n\n⚖️ DECISIONE AGENTE: ANSWERABLE | CAUSA PRIMARIA: None\n💬 RISPOSTA FINALE: \"Centralized imperial government (Ming and Qing dynasties)\"\n\n📝 SPIEGAZIONE DELLA CAUSA:\n\"The document does not contain any visible text or information regarding China's government type during the 1500s-1700s, making it impossible to confirm or reject the value mismatch.\"\n\n🔍 EVIDENZE ESTRATTE DAL DOCUMENTO: [p.1 Q2] During the 16th and 17th centuries, China was governed by the Ming and Qing dynasties, representing a centralized imperial government.\n⚙️ PROMPT USATI: question_analysis_v1, nlp_tag_cot, docel_cot_v4, nlp_list_ocr_cot, nlp_list_ocr_cot, answerability_verifier_v1, nlp_tag_cot");

  var q1_39 = form.addMultipleChoiceItem();
  q1_39.setTitle("#39.1 - La spiegazione circa la causa di unanswerability è corretta?");
  q1_39.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q1_39.setRequired(true);

  var q2_39 = form.addMultipleChoiceItem();
  q2_39.setTitle("#39.2 - La spiegazione circa la causa di unanswerability è completa?");
  q2_39.setChoiceValues(["Sì", "No"]);
  q2_39.showOtherOption(true); // Permette di specificare cosa manca
  q2_39.setRequired(true);

  var q3_39 = form.addMultipleChoiceItem();
  q3_39.setTitle("#39.3 - La spiegazione contiene riferimenti corretti alle parti di documento coinvolte?");
  q3_39.setChoiceValues(["Sì", "No", "Parzialmente", "Non applicabile (nessun riferimento necessario)"]);
  q3_39.setRequired(true);

  var q4_39 = form.addMultipleChoiceItem();
  q4_39.setTitle("#39.4 - La spiegazione contiene tutti i riferimenti completi alle parti di documento coinvolte?");
  q4_39.setChoiceValues(["Sì", "No", "Non applicabile"]);
  q4_39.showOtherOption(true); // Permette di specificare cosa manca
  q4_39.setRequired(true);

  var q5_39 = form.addMultipleChoiceItem();
  q5_39.setTitle("#39.5 - La spiegazione contiene riferimenti corretti alle parti di domanda che sono causa di unanswerability?");
  q5_39.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q5_39.setRequired(true);

  var q6_39 = form.addMultipleChoiceItem();
  q6_39.setTitle("#39.6 - La spiegazione contiene tutti i riferimenti completi alle parti di domanda che sono causa di unanswerability?");
  q6_39.setChoiceValues(["Sì", "No"]);
  q6_39.showOtherOption(true); // Permette di specificare cosa manca
  q6_39.setRequired(true);

  // ================= ITEM #40 =================
  var pageBreak = form.addPageBreakItem();
  pageBreak.setTitle("Item #40 — [Location Corruption] (postal_code_information - C1)");
  pageBreak.setHelpText("❓ DOMANDA CORROTTA: \"What is the gj26 office number?\"\n📌 DOMANDA ORIGINALE: \"What is the Virginia office number?\"\n\n⚖️ DECISIONE AGENTE: ANSWERABLE | CAUSA PRIMARIA: None\n💬 RISPOSTA FINALE: \"456\"\n\n📝 SPIEGAZIONE DELLA CAUSA:\n\"No document content was provided in the OCR section, making it impossible to locate or verify the existence or format of the gj26 office number.\"\n\n🔍 EVIDENZE ESTRATTE DAL DOCUMENTO: [p.1 Q3] gj26 Office: 456\n⚙️ PROMPT USATI: question_analysis_v1, nlp_tag_cot, docel_cot_v4, nlp_list_ocr_cot, nlp_list_ocr_cot, answerability_verifier_v1, nlp_tag_cot");

  var q1_40 = form.addMultipleChoiceItem();
  q1_40.setTitle("#40.1 - La spiegazione circa la causa di unanswerability è corretta?");
  q1_40.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q1_40.setRequired(true);

  var q2_40 = form.addMultipleChoiceItem();
  q2_40.setTitle("#40.2 - La spiegazione circa la causa di unanswerability è completa?");
  q2_40.setChoiceValues(["Sì", "No"]);
  q2_40.showOtherOption(true); // Permette di specificare cosa manca
  q2_40.setRequired(true);

  var q3_40 = form.addMultipleChoiceItem();
  q3_40.setTitle("#40.3 - La spiegazione contiene riferimenti corretti alle parti di documento coinvolte?");
  q3_40.setChoiceValues(["Sì", "No", "Parzialmente", "Non applicabile (nessun riferimento necessario)"]);
  q3_40.setRequired(true);

  var q4_40 = form.addMultipleChoiceItem();
  q4_40.setTitle("#40.4 - La spiegazione contiene tutti i riferimenti completi alle parti di documento coinvolte?");
  q4_40.setChoiceValues(["Sì", "No", "Non applicabile"]);
  q4_40.showOtherOption(true); // Permette di specificare cosa manca
  q4_40.setRequired(true);

  var q5_40 = form.addMultipleChoiceItem();
  q5_40.setTitle("#40.5 - La spiegazione contiene riferimenti corretti alle parti di domanda che sono causa di unanswerability?");
  q5_40.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q5_40.setRequired(true);

  var q6_40 = form.addMultipleChoiceItem();
  q6_40.setTitle("#40.6 - La spiegazione contiene tutti i riferimenti completi alle parti di domanda che sono causa di unanswerability?");
  q6_40.setChoiceValues(["Sì", "No"]);
  q6_40.showOtherOption(true); // Permette di specificare cosa manca
  q6_40.setRequired(true);

  // ================= ITEM #41 =================
  var pageBreak = form.addPageBreakItem();
  pageBreak.setTitle("Item #41 — [Document Structure Corruption] (document_element_information - C3)");
  pageBreak.setHelpText("❓ DOMANDA CORROTTA: \"In the text of page1of4, what has been suggested for text as word study?\"\n📌 DOMANDA ORIGINALE: \"In the lesson preparation table of page 1, what has been suggested for vocabulary of instruction as word study?\"\n\n⚖️ DECISIONE AGENTE: INSUFFICIENT_EVIDENCE | CAUSA PRIMARIA: None\n💬 RISPOSTA FINALE: \"Unable to determine\"\n\n📝 SPIEGAZIONE DELLA CAUSA:\n\"The suggested content for Word Study is clearly visible in the table on page 1, listing 'Alphabetize, High-frequency word' under Vocabulary of Instruction and 'Chart paper (if applicable)' under Materials.\"\n\n🔍 EVIDENZE ESTRATTE DAL DOCUMENTO: [p.1 Q3] Word Study Vocabulary of Instruction: Alphabetize, High-frequency word Materials: Chart paper (if applicable)\n⚙️ PROMPT USATI: question_analysis_v1, layout_v4, nlp_tag_cot, docel_cot_v4, nlp_list_ocr_cot, answerability_verifier_v1, nlp_tag_cot");

  var q1_41 = form.addMultipleChoiceItem();
  q1_41.setTitle("#41.1 - La spiegazione circa la causa di unanswerability è corretta?");
  q1_41.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q1_41.setRequired(true);

  var q2_41 = form.addMultipleChoiceItem();
  q2_41.setTitle("#41.2 - La spiegazione circa la causa di unanswerability è completa?");
  q2_41.setChoiceValues(["Sì", "No"]);
  q2_41.showOtherOption(true); // Permette di specificare cosa manca
  q2_41.setRequired(true);

  var q3_41 = form.addMultipleChoiceItem();
  q3_41.setTitle("#41.3 - La spiegazione contiene riferimenti corretti alle parti di documento coinvolte?");
  q3_41.setChoiceValues(["Sì", "No", "Parzialmente", "Non applicabile (nessun riferimento necessario)"]);
  q3_41.setRequired(true);

  var q4_41 = form.addMultipleChoiceItem();
  q4_41.setTitle("#41.4 - La spiegazione contiene tutti i riferimenti completi alle parti di documento coinvolte?");
  q4_41.setChoiceValues(["Sì", "No", "Non applicabile"]);
  q4_41.showOtherOption(true); // Permette di specificare cosa manca
  q4_41.setRequired(true);

  var q5_41 = form.addMultipleChoiceItem();
  q5_41.setTitle("#41.5 - La spiegazione contiene riferimenti corretti alle parti di domanda che sono causa di unanswerability?");
  q5_41.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q5_41.setRequired(true);

  var q6_41 = form.addMultipleChoiceItem();
  q6_41.setTitle("#41.6 - La spiegazione contiene tutti i riferimenti completi alle parti di domanda che sono causa di unanswerability?");
  q6_41.setChoiceValues(["Sì", "No"]);
  q6_41.showOtherOption(true); // Permette di specificare cosa manca
  q6_41.setRequired(true);

  // ================= ITEM #42 =================
  var pageBreak = form.addPageBreakItem();
  pageBreak.setTitle("Item #42 — [Document Structure Corruption] (document_element_type - C1)");
  pageBreak.setHelpText("❓ DOMANDA CORROTTA: \"On page six, what month is included in the introduction to the second to last question?\"\n📌 DOMANDA ORIGINALE: \"On page six, what month is included in the answer to the second to last question?\"\n\n⚖️ DECISIONE AGENTE: UNANSWERABLE | CAUSA PRIMARIA: UNSUPPORTED_PRESUPPOSITION\n💬 RISPOSTA FINALE: \"Unable to determine\"\n\n📝 SPIEGAZIONE DELLA CAUSA:\n\"The question presupposes that a month is included in the introduction to the second to last question on page six. Examination of page six reveals that while the structure for the second to last question is present, the introduction text does not contain any identifiable month.\"\n\n🔍 EVIDENZE ESTRATTE DAL DOCUMENTO: [p.6 Q3] The introduction to the second to last question (Q3) on page six does not contain any explicit mention of a month.\n⚙️ PROMPT USATI: question_analysis_v1, layout_v4, nlp_tag_cot, nlp_tag_cot, docel_cot_v4");

  var q1_42 = form.addMultipleChoiceItem();
  q1_42.setTitle("#42.1 - La spiegazione circa la causa di unanswerability è corretta?");
  q1_42.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q1_42.setRequired(true);

  var q2_42 = form.addMultipleChoiceItem();
  q2_42.setTitle("#42.2 - La spiegazione circa la causa di unanswerability è completa?");
  q2_42.setChoiceValues(["Sì", "No"]);
  q2_42.showOtherOption(true); // Permette di specificare cosa manca
  q2_42.setRequired(true);

  var q3_42 = form.addMultipleChoiceItem();
  q3_42.setTitle("#42.3 - La spiegazione contiene riferimenti corretti alle parti di documento coinvolte?");
  q3_42.setChoiceValues(["Sì", "No", "Parzialmente", "Non applicabile (nessun riferimento necessario)"]);
  q3_42.setRequired(true);

  var q4_42 = form.addMultipleChoiceItem();
  q4_42.setTitle("#42.4 - La spiegazione contiene tutti i riferimenti completi alle parti di documento coinvolte?");
  q4_42.setChoiceValues(["Sì", "No", "Non applicabile"]);
  q4_42.showOtherOption(true); // Permette di specificare cosa manca
  q4_42.setRequired(true);

  var q5_42 = form.addMultipleChoiceItem();
  q5_42.setTitle("#42.5 - La spiegazione contiene riferimenti corretti alle parti di domanda che sono causa di unanswerability?");
  q5_42.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q5_42.setRequired(true);

  var q6_42 = form.addMultipleChoiceItem();
  q6_42.setTitle("#42.6 - La spiegazione contiene tutti i riferimenti completi alle parti di domanda che sono causa di unanswerability?");
  q6_42.setChoiceValues(["Sì", "No"]);
  q6_42.showOtherOption(true); // Permette di specificare cosa manca
  q6_42.setRequired(true);

  // ================= ITEM #43 =================
  var pageBreak = form.addPageBreakItem();
  pageBreak.setTitle("Item #43 — [Document Structure Corruption] (document_position_information - C1)");
  pageBreak.setHelpText("❓ DOMANDA CORROTTA: \"What is the memo number for the Apollo project noted on the next page?\"\n📌 DOMANDA ORIGINALE: \"What the is the memo number for the Apollo project noted on the first page?\"\n\n⚖️ DECISIONE AGENTE: UNANSWERABLE | CAUSA PRIMARIA: SPATIAL_MISMATCH\n💬 RISPOSTA FINALE: \"Unable to determine\"\n\n📝 SPIEGAZIONE DELLA CAUSA:\n\"The memo number for the Apollo project (1933) is clearly visible on the current page (Page 1), contradicting the question's premise that the information is located on the next page.\"\n\n🔍 EVIDENZE ESTRATTE DAL DOCUMENTO: [p.1 Q2] Apollo Project Memo No. 1933\n⚙️ PROMPT USATI: question_analysis_v1, layout_v4");

  var q1_43 = form.addMultipleChoiceItem();
  q1_43.setTitle("#43.1 - La spiegazione circa la causa di unanswerability è corretta?");
  q1_43.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q1_43.setRequired(true);

  var q2_43 = form.addMultipleChoiceItem();
  q2_43.setTitle("#43.2 - La spiegazione circa la causa di unanswerability è completa?");
  q2_43.setChoiceValues(["Sì", "No"]);
  q2_43.showOtherOption(true); // Permette di specificare cosa manca
  q2_43.setRequired(true);

  var q3_43 = form.addMultipleChoiceItem();
  q3_43.setTitle("#43.3 - La spiegazione contiene riferimenti corretti alle parti di documento coinvolte?");
  q3_43.setChoiceValues(["Sì", "No", "Parzialmente", "Non applicabile (nessun riferimento necessario)"]);
  q3_43.setRequired(true);

  var q4_43 = form.addMultipleChoiceItem();
  q4_43.setTitle("#43.4 - La spiegazione contiene tutti i riferimenti completi alle parti di documento coinvolte?");
  q4_43.setChoiceValues(["Sì", "No", "Non applicabile"]);
  q4_43.showOtherOption(true); // Permette di specificare cosa manca
  q4_43.setRequired(true);

  var q5_43 = form.addMultipleChoiceItem();
  q5_43.setTitle("#43.5 - La spiegazione contiene riferimenti corretti alle parti di domanda che sono causa di unanswerability?");
  q5_43.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q5_43.setRequired(true);

  var q6_43 = form.addMultipleChoiceItem();
  q6_43.setTitle("#43.6 - La spiegazione contiene tutti i riferimenti completi alle parti di domanda che sono causa di unanswerability?");
  q6_43.setChoiceValues(["Sì", "No"]);
  q6_43.showOtherOption(true); // Permette di specificare cosa manca
  q6_43.setRequired(true);

  // ================= ITEM #44 =================
  var pageBreak = form.addPageBreakItem();
  pageBreak.setTitle("Item #44 — [Document Structure Corruption] (document_element_information - C3)");
  pageBreak.setHelpText("❓ DOMANDA CORROTTA: \"In the text of page1of4, what has been suggested for key understandings as word study?\"\n📌 DOMANDA ORIGINALE: \"In the lesson preparation table of page 1, what has been suggested for vocabulary of instruction as word study?\"\n\n⚖️ DECISIONE AGENTE: INSUFFICIENT_EVIDENCE | CAUSA PRIMARIA: None\n💬 RISPOSTA FINALE: \"Unable to determine\"\n\n📝 SPIEGAZIONE DELLA CAUSA:\n\"The information regarding key understandings for Word Study is clearly visible in the table on page 1 of 4, making a spatial mismatch cause incorrect.\"\n\n🔍 EVIDENZE ESTRATTE DAL DOCUMENTO: [p.1 Q3] Key Understandings and Guiding Questions | Word Study | Key Understandings: | Guiding Questions: How is alphabetizing helpful in learning?\n⚙️ PROMPT USATI: question_analysis_v1, layout_v4, nlp_tag_cot, docel_cot_v4, nlp_list_ocr_cot, nlp_tag_cot");

  var q1_44 = form.addMultipleChoiceItem();
  q1_44.setTitle("#44.1 - La spiegazione circa la causa di unanswerability è corretta?");
  q1_44.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q1_44.setRequired(true);

  var q2_44 = form.addMultipleChoiceItem();
  q2_44.setTitle("#44.2 - La spiegazione circa la causa di unanswerability è completa?");
  q2_44.setChoiceValues(["Sì", "No"]);
  q2_44.showOtherOption(true); // Permette di specificare cosa manca
  q2_44.setRequired(true);

  var q3_44 = form.addMultipleChoiceItem();
  q3_44.setTitle("#44.3 - La spiegazione contiene riferimenti corretti alle parti di documento coinvolte?");
  q3_44.setChoiceValues(["Sì", "No", "Parzialmente", "Non applicabile (nessun riferimento necessario)"]);
  q3_44.setRequired(true);

  var q4_44 = form.addMultipleChoiceItem();
  q4_44.setTitle("#44.4 - La spiegazione contiene tutti i riferimenti completi alle parti di documento coinvolte?");
  q4_44.setChoiceValues(["Sì", "No", "Non applicabile"]);
  q4_44.showOtherOption(true); // Permette di specificare cosa manca
  q4_44.setRequired(true);

  var q5_44 = form.addMultipleChoiceItem();
  q5_44.setTitle("#44.5 - La spiegazione contiene riferimenti corretti alle parti di domanda che sono causa di unanswerability?");
  q5_44.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q5_44.setRequired(true);

  var q6_44 = form.addMultipleChoiceItem();
  q6_44.setTitle("#44.6 - La spiegazione contiene tutti i riferimenti completi alle parti di domanda che sono causa di unanswerability?");
  q6_44.setChoiceValues(["Sì", "No"]);
  q6_44.showOtherOption(true); // Permette di specificare cosa manca
  q6_44.setRequired(true);

  // ================= ITEM #45 =================
  var pageBreak = form.addPageBreakItem();
  pageBreak.setTitle("Item #45 — [Document Structure Corruption] (document_element_type - C1)");
  pageBreak.setHelpText("❓ DOMANDA CORROTTA: \"What is the cost of the unused budgeted items mentioned in the document?\"\n📌 DOMANDA ORIGINALE: \"What is the cost of the materials mentioned in the document?\"\n\n⚖️ DECISIONE AGENTE: UNANSWERABLE | CAUSA PRIMARIA: DOCUMENT_ELEMENT_MISMATCH\n💬 RISPOSTA FINALE: \"Unable to determine\"\n\n📝 SPIEGAZIONE DELLA CAUSA:\n\"While the document mentions that funds have been identified from unused budgeted items, it does not provide a specific monetary cost or value for these unused budgeted items.\"\n\n🔍 EVIDENZE ESTRATTE DAL DOCUMENTO: [p.1 Q3] Funds have been identified from unused budgeted items for this expense if approved.\n⚙️ PROMPT USATI: question_analysis_v1, layout_v4, layout_v4");

  var q1_45 = form.addMultipleChoiceItem();
  q1_45.setTitle("#45.1 - La spiegazione circa la causa di unanswerability è corretta?");
  q1_45.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q1_45.setRequired(true);

  var q2_45 = form.addMultipleChoiceItem();
  q2_45.setTitle("#45.2 - La spiegazione circa la causa di unanswerability è completa?");
  q2_45.setChoiceValues(["Sì", "No"]);
  q2_45.showOtherOption(true); // Permette di specificare cosa manca
  q2_45.setRequired(true);

  var q3_45 = form.addMultipleChoiceItem();
  q3_45.setTitle("#45.3 - La spiegazione contiene riferimenti corretti alle parti di documento coinvolte?");
  q3_45.setChoiceValues(["Sì", "No", "Parzialmente", "Non applicabile (nessun riferimento necessario)"]);
  q3_45.setRequired(true);

  var q4_45 = form.addMultipleChoiceItem();
  q4_45.setTitle("#45.4 - La spiegazione contiene tutti i riferimenti completi alle parti di documento coinvolte?");
  q4_45.setChoiceValues(["Sì", "No", "Non applicabile"]);
  q4_45.showOtherOption(true); // Permette di specificare cosa manca
  q4_45.setRequired(true);

  var q5_45 = form.addMultipleChoiceItem();
  q5_45.setTitle("#45.5 - La spiegazione contiene riferimenti corretti alle parti di domanda che sono causa di unanswerability?");
  q5_45.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q5_45.setRequired(true);

  var q6_45 = form.addMultipleChoiceItem();
  q6_45.setTitle("#45.6 - La spiegazione contiene tutti i riferimenti completi alle parti di domanda che sono causa di unanswerability?");
  q6_45.setChoiceValues(["Sì", "No"]);
  q6_45.showOtherOption(true); // Permette di specificare cosa manca
  q6_45.setRequired(true);

  // ================= ITEM #46 =================
  var pageBreak = form.addPageBreakItem();
  pageBreak.setTitle("Item #46 — [Document Structure Corruption] (document_position_information - C1)");
  pageBreak.setHelpText("❓ DOMANDA CORROTTA: \"What is the memo number for the Apollo project noted at the bottom?\"\n📌 DOMANDA ORIGINALE: \"What the is the memo number for the Apollo project noted on the first page?\"\n\n⚖️ DECISIONE AGENTE: INSUFFICIENT_EVIDENCE | CAUSA PRIMARIA: None\n💬 RISPOSTA FINALE: \"Unable to determine\"\n\n📝 SPIEGAZIONE DELLA CAUSA:\n\"The memo number for the Apollo project, '1933', is clearly visible on Page 1. Therefore, the cause is not a spatial mismatch, as the information is present in the document.\"\n\n🔍 EVIDENZE ESTRATTE DAL DOCUMENTO: (Nessuna evidenza estratta)\n⚙️ PROMPT USATI: question_analysis_v1, layout_v4, nlp_tag_cot, docel_cot_v4, nlp_list_ocr_cot, answerability_verifier_v1, nlp_tag_cot");

  var q1_46 = form.addMultipleChoiceItem();
  q1_46.setTitle("#46.1 - La spiegazione circa la causa di unanswerability è corretta?");
  q1_46.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q1_46.setRequired(true);

  var q2_46 = form.addMultipleChoiceItem();
  q2_46.setTitle("#46.2 - La spiegazione circa la causa di unanswerability è completa?");
  q2_46.setChoiceValues(["Sì", "No"]);
  q2_46.showOtherOption(true); // Permette di specificare cosa manca
  q2_46.setRequired(true);

  var q3_46 = form.addMultipleChoiceItem();
  q3_46.setTitle("#46.3 - La spiegazione contiene riferimenti corretti alle parti di documento coinvolte?");
  q3_46.setChoiceValues(["Sì", "No", "Parzialmente", "Non applicabile (nessun riferimento necessario)"]);
  q3_46.setRequired(true);

  var q4_46 = form.addMultipleChoiceItem();
  q4_46.setTitle("#46.4 - La spiegazione contiene tutti i riferimenti completi alle parti di documento coinvolte?");
  q4_46.setChoiceValues(["Sì", "No", "Non applicabile"]);
  q4_46.showOtherOption(true); // Permette di specificare cosa manca
  q4_46.setRequired(true);

  var q5_46 = form.addMultipleChoiceItem();
  q5_46.setTitle("#46.5 - La spiegazione contiene riferimenti corretti alle parti di domanda che sono causa di unanswerability?");
  q5_46.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q5_46.setRequired(true);

  var q6_46 = form.addMultipleChoiceItem();
  q6_46.setTitle("#46.6 - La spiegazione contiene tutti i riferimenti completi alle parti di domanda che sono causa di unanswerability?");
  q6_46.setChoiceValues(["Sì", "No"]);
  q6_46.showOtherOption(true); // Permette di specificare cosa manca
  q6_46.setRequired(true);

  // ================= ITEM #47 =================
  var pageBreak = form.addPageBreakItem();
  pageBreak.setTitle("Item #47 — [Document Structure Corruption] (document_element_type - C1)");
  pageBreak.setHelpText("❓ DOMANDA CORROTTA: \"How many Inspector General administrative subpoenas were issued to obtain memoranda of review and records?\"\n📌 DOMANDA ORIGINALE: \"How many Inspector General administrative subpoenas to obtain foreclosure-related documents and records?\"\n\n⚖️ DECISIONE AGENTE: INSUFFICIENT_EVIDENCE | CAUSA PRIMARIA: None\n💬 RISPOSTA FINALE: \"Unable to determine\"\n\n📝 SPIEGAZIONE DELLA CAUSA:\n\"The document content is not visible, making it impossible to locate the specific count of Inspector General administrative subpoenas related to memoranda of review and records, thus preventing confirmation of a value mismatch.\"\n\n🔍 EVIDENZE ESTRATTE DAL DOCUMENTO: (Nessuna evidenza estratta)\n⚙️ PROMPT USATI: question_analysis_v1, nlp_tag_cot, docel_cot_v4, nlp_list_ocr_cot, nlp_list_ocr_cot, answerability_verifier_v1, nlp_tag_cot");

  var q1_47 = form.addMultipleChoiceItem();
  q1_47.setTitle("#47.1 - La spiegazione circa la causa di unanswerability è corretta?");
  q1_47.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q1_47.setRequired(true);

  var q2_47 = form.addMultipleChoiceItem();
  q2_47.setTitle("#47.2 - La spiegazione circa la causa di unanswerability è completa?");
  q2_47.setChoiceValues(["Sì", "No"]);
  q2_47.showOtherOption(true); // Permette di specificare cosa manca
  q2_47.setRequired(true);

  var q3_47 = form.addMultipleChoiceItem();
  q3_47.setTitle("#47.3 - La spiegazione contiene riferimenti corretti alle parti di documento coinvolte?");
  q3_47.setChoiceValues(["Sì", "No", "Parzialmente", "Non applicabile (nessun riferimento necessario)"]);
  q3_47.setRequired(true);

  var q4_47 = form.addMultipleChoiceItem();
  q4_47.setTitle("#47.4 - La spiegazione contiene tutti i riferimenti completi alle parti di documento coinvolte?");
  q4_47.setChoiceValues(["Sì", "No", "Non applicabile"]);
  q4_47.showOtherOption(true); // Permette di specificare cosa manca
  q4_47.setRequired(true);

  var q5_47 = form.addMultipleChoiceItem();
  q5_47.setTitle("#47.5 - La spiegazione contiene riferimenti corretti alle parti di domanda che sono causa di unanswerability?");
  q5_47.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q5_47.setRequired(true);

  var q6_47 = form.addMultipleChoiceItem();
  q6_47.setTitle("#47.6 - La spiegazione contiene tutti i riferimenti completi alle parti di domanda che sono causa di unanswerability?");
  q6_47.setChoiceValues(["Sì", "No"]);
  q6_47.showOtherOption(true); // Permette di specificare cosa manca
  q6_47.setRequired(true);

  // ================= ITEM #48 =================
  var pageBreak = form.addPageBreakItem();
  pageBreak.setTitle("Item #48 — [Document Structure Corruption] (document_element_type - C3)");
  pageBreak.setHelpText("❓ DOMANDA CORROTTA: \"In the financial summary on page 1 of 8, what were the salaries and wages for year 5?\"\n📌 DOMANDA ORIGINALE: \"In the table on page 7 what were the salaries and wages for year five?\"\n\n⚖️ DECISIONE AGENTE: UNANSWERABLE | CAUSA PRIMARIA: SPATIAL_MISMATCH\n💬 RISPOSTA FINALE: \"Unable to determine\"\n\n📝 SPIEGAZIONE DELLA CAUSA:\n\"The question incorrectly specifies that the financial summary is on page 1. The required data for 'Salaries and Wages' for 'Year 5' is actually located in the financial summary tables on Page 2 and Page 8, not Page 1.\"\n\n🔍 EVIDENZE ESTRATTE DAL DOCUMENTO: [p.2 Q3] Salaries and Wages | $272,938 | [p.8 Q3] Salaries and Wages | $272,938\n⚙️ PROMPT USATI: question_analysis_v1, layout_v4");

  var q1_48 = form.addMultipleChoiceItem();
  q1_48.setTitle("#48.1 - La spiegazione circa la causa di unanswerability è corretta?");
  q1_48.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q1_48.setRequired(true);

  var q2_48 = form.addMultipleChoiceItem();
  q2_48.setTitle("#48.2 - La spiegazione circa la causa di unanswerability è completa?");
  q2_48.setChoiceValues(["Sì", "No"]);
  q2_48.showOtherOption(true); // Permette di specificare cosa manca
  q2_48.setRequired(true);

  var q3_48 = form.addMultipleChoiceItem();
  q3_48.setTitle("#48.3 - La spiegazione contiene riferimenti corretti alle parti di documento coinvolte?");
  q3_48.setChoiceValues(["Sì", "No", "Parzialmente", "Non applicabile (nessun riferimento necessario)"]);
  q3_48.setRequired(true);

  var q4_48 = form.addMultipleChoiceItem();
  q4_48.setTitle("#48.4 - La spiegazione contiene tutti i riferimenti completi alle parti di documento coinvolte?");
  q4_48.setChoiceValues(["Sì", "No", "Non applicabile"]);
  q4_48.showOtherOption(true); // Permette di specificare cosa manca
  q4_48.setRequired(true);

  var q5_48 = form.addMultipleChoiceItem();
  q5_48.setTitle("#48.5 - La spiegazione contiene riferimenti corretti alle parti di domanda che sono causa di unanswerability?");
  q5_48.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q5_48.setRequired(true);

  var q6_48 = form.addMultipleChoiceItem();
  q6_48.setTitle("#48.6 - La spiegazione contiene tutti i riferimenti completi alle parti di domanda che sono causa di unanswerability?");
  q6_48.setChoiceValues(["Sì", "No"]);
  q6_48.showOtherOption(true); // Permette di specificare cosa manca
  q6_48.setRequired(true);

  // ================= ITEM #49 =================
  var pageBreak = form.addPageBreakItem();
  pageBreak.setTitle("Item #49 — [Document Structure Corruption] (document_element_type - C1)");
  pageBreak.setHelpText("❓ DOMANDA CORROTTA: \"What is the middle line of the columns?\"\n📌 DOMANDA ORIGINALE: \"What is the middle line of receipt?\"\n\n⚖️ DECISIONE AGENTE: INSUFFICIENT_EVIDENCE | CAUSA PRIMARIA: None\n💬 RISPOSTA FINALE: \"Unable to determine\"\n\n📝 SPIEGAZIONE DELLA CAUSA:\n\"The document clearly contains multiple tables, columns, and lines, meaning the elements referenced in the question are spatially present. Therefore, the candidate cause of SPATIAL_MISMATCH is rejected.\"\n\n🔍 EVIDENZE ESTRATTE DAL DOCUMENTO: (Nessuna evidenza estratta)\n⚙️ PROMPT USATI: question_analysis_v1, layout_v4, docel_cot_v4, nlp_list_ocr_cot, nlp_list_ocr_cot, answerability_verifier_v1, nlp_tag_cot");

  var q1_49 = form.addMultipleChoiceItem();
  q1_49.setTitle("#49.1 - La spiegazione circa la causa di unanswerability è corretta?");
  q1_49.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q1_49.setRequired(true);

  var q2_49 = form.addMultipleChoiceItem();
  q2_49.setTitle("#49.2 - La spiegazione circa la causa di unanswerability è completa?");
  q2_49.setChoiceValues(["Sì", "No"]);
  q2_49.showOtherOption(true); // Permette di specificare cosa manca
  q2_49.setRequired(true);

  var q3_49 = form.addMultipleChoiceItem();
  q3_49.setTitle("#49.3 - La spiegazione contiene riferimenti corretti alle parti di documento coinvolte?");
  q3_49.setChoiceValues(["Sì", "No", "Parzialmente", "Non applicabile (nessun riferimento necessario)"]);
  q3_49.setRequired(true);

  var q4_49 = form.addMultipleChoiceItem();
  q4_49.setTitle("#49.4 - La spiegazione contiene tutti i riferimenti completi alle parti di documento coinvolte?");
  q4_49.setChoiceValues(["Sì", "No", "Non applicabile"]);
  q4_49.showOtherOption(true); // Permette di specificare cosa manca
  q4_49.setRequired(true);

  var q5_49 = form.addMultipleChoiceItem();
  q5_49.setTitle("#49.5 - La spiegazione contiene riferimenti corretti alle parti di domanda che sono causa di unanswerability?");
  q5_49.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q5_49.setRequired(true);

  var q6_49 = form.addMultipleChoiceItem();
  q6_49.setTitle("#49.6 - La spiegazione contiene tutti i riferimenti completi alle parti di domanda che sono causa di unanswerability?");
  q6_49.setChoiceValues(["Sì", "No"]);
  q6_49.showOtherOption(true); // Permette di specificare cosa manca
  q6_49.setRequired(true);

  // ================= ITEM #50 =================
  var pageBreak = form.addPageBreakItem();
  pageBreak.setTitle("Item #50 — [Document Structure Corruption] (document_element_type - C1)");
  pageBreak.setHelpText("❓ DOMANDA CORROTTA: \"How many Inspector General administrative subpoenas to obtain foreclosure-related documents and sworn documents?\"\n📌 DOMANDA ORIGINALE: \"How many Inspector General administrative subpoenas to obtain foreclosure-related documents and records?\"\n\n⚖️ DECISIONE AGENTE: ANSWERABLE | CAUSA PRIMARIA: None\n💬 RISPOSTA FINALE: \"19\"\n\n📝 SPIEGAZIONE DELLA CAUSA:\n\"The document explicitly states the number of subpoenas on Page 3, making a spatial mismatch claim incorrect. The count is directly visible in the text.\"\n\n🔍 EVIDENZE ESTRATTE DAL DOCUMENTO: [p.3 Q2] The OIG issued 19 administrative subpoenas to obtain foreclosure-related documents and sworn documents.\n⚙️ PROMPT USATI: question_analysis_v1, layout_v4, nlp_tag_cot, docel_cot_v4, nlp_list_ocr_cot, answerability_verifier_v1, nlp_tag_cot");

  var q1_50 = form.addMultipleChoiceItem();
  q1_50.setTitle("#50.1 - La spiegazione circa la causa di unanswerability è corretta?");
  q1_50.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q1_50.setRequired(true);

  var q2_50 = form.addMultipleChoiceItem();
  q2_50.setTitle("#50.2 - La spiegazione circa la causa di unanswerability è completa?");
  q2_50.setChoiceValues(["Sì", "No"]);
  q2_50.showOtherOption(true); // Permette di specificare cosa manca
  q2_50.setRequired(true);

  var q3_50 = form.addMultipleChoiceItem();
  q3_50.setTitle("#50.3 - La spiegazione contiene riferimenti corretti alle parti di documento coinvolte?");
  q3_50.setChoiceValues(["Sì", "No", "Parzialmente", "Non applicabile (nessun riferimento necessario)"]);
  q3_50.setRequired(true);

  var q4_50 = form.addMultipleChoiceItem();
  q4_50.setTitle("#50.4 - La spiegazione contiene tutti i riferimenti completi alle parti di documento coinvolte?");
  q4_50.setChoiceValues(["Sì", "No", "Non applicabile"]);
  q4_50.showOtherOption(true); // Permette di specificare cosa manca
  q4_50.setRequired(true);

  var q5_50 = form.addMultipleChoiceItem();
  q5_50.setTitle("#50.5 - La spiegazione contiene riferimenti corretti alle parti di domanda che sono causa di unanswerability?");
  q5_50.setChoiceValues(["Sì", "No", "Parzialmente"]);
  q5_50.setRequired(true);

  var q6_50 = form.addMultipleChoiceItem();
  q6_50.setTitle("#50.6 - La spiegazione contiene tutti i riferimenti completi alle parti di domanda che sono causa di unanswerability?");
  q6_50.setChoiceValues(["Sì", "No"]);
  q6_50.showOtherOption(true); // Permette di specificare cosa manca
  q6_50.setRequired(true);

  Logger.log("✅ Google Form creato con successo!");
  Logger.log("🔗 Link per modificare il modulo: " + form.getEditUrl());
  Logger.log("🔗 Link per compilare il modulo: " + form.getPublishedUrl());
}