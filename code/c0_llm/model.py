#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：project-2 
@File    ：model.py
@IDE     ：PyCharm 
@Author  ：李林名
@Date    ：2025/4/27 15:17 
@Usage   ：
'''

# # 本地推理模型：DeepSeek-R1-Distill-Qwen-32B
import openai
#
# client = openai.Client(api_key="not empty", base_url="http://10.160.199.27:30535/v1")
# model_uid = "DeepSeek-R1-Distill-Qwen-32B"
#
# response = client.chat.completions.create(
#     model=model_uid,
#     messages=[
#         {
#             "content": "3.11和3.9哪个大",
#             "role": "user",
#         }
#     ],
#     max_tokens=20000
# )
# print(response.choices[0].message.content)


# Qwen2.5-72B-Instruct
import openai
client = openai.Client(api_key="not empty", base_url="http://10.160.199.27:30535/v1")


# prompt = r"""
# 角色：你是一个语言学专家
# 任务：你当前的任务是补充问题的完整性，使得问题完整无歧义，无缺乏主语或者实体，类似数据库中ID，独立且唯一标识。
# 注意：1. 可以采用who（主体）、when（时间）、where（地点）、why、what（对象）、how（方法）的分析框架。
#      2. 包括研究主体、研究对象、研究时间、研究地点、研究目的、技术类型、相关细节。
#      3. 输出的补充完整语义的问题，请使用中文。
#
# ## 输出格式：
#  - JSON 数组格式必须正确
# - 字段名使用英文双引号
# - 输出的 JSON 数组必须严格符合以下结构：
# - 对于人名、地名等名称，在提取问题的时候，必须使用英文（中文翻译）方式保留准确性和可读性。比如：英文名称（中文名称）。
# ```json
# ["问题1", "问题2", "..."]
# ```
#
# ## 示例
# # 样例1:
# # 原始问题：
# 在现场分析中采用了哪些非侵入性成像技术？
# # 完整语义的问题：
# 在2014-2015年意大利考古团队（MAIER）对土耳其Hierapolis of Phrygia（弗里吉亚的希拉波利斯）考古遗址出土的Severan Theatre（塞维鲁剧院）和North Agora（北广场）大理石雕像的现场分析中，研究者采用了哪些非侵入性成像技术来检测古代彩绘痕迹？
#
# # 样例2:
# # 原始问题：
# 研究使用的非侵入性成像技术包括哪些类型？
# # 完整语义的问题：
# 在2014-2015年意大利考古团队（MAIER）对土耳其Hierapolis of Phrygia（赫拉波利斯）遗址的Severan Theatre（塞维鲁剧院）和North Agora（北广场）出土的大理石雕像进行多学科研究中，采用了哪些非侵入性成像技术来检测和分析雕像表面的古代彩绘痕迹？
#
# # 样例3:
# # 原始问题：
# 对Hierapolis（希拉波利斯）雕像进行微破坏的理由是什么？
# # 完整语义的问题：
# 在2014-2015年土耳其Hierapolis（希拉波利斯）考古遗址的雕像研究中，意大利考古团队MAIER为何在非侵入性成像技术（如UVf和VIL）无法完全表征有机染料（如茜素湖）时，对Kore-Persephone雕像和Attis雕像进行微破坏取样？
#
#
# ## 初始问题
# [
#   "Hierapolis of Phrygia（弗里吉亚的希拉波利斯）出土的大理石雕像上使用了哪些主要的着色材料？",
#   "Severan Theatre（塞维兰剧院）的浮雕和装饰雕像上发现了哪些色彩痕迹？",
#   "雕像中的女性形象代表了什么样的文化意义？",
#   "研究中应用了哪些非侵入性成像技术来检测雕像上的颜色痕迹？",
#   "Hierapolis of Phrygia（弗里吉亚的希拉波利斯）的哪些雕像被保存在了Hierapolis-Pamukkale博物馆？",
#   "Hierapolis of Phrygia（弗里吉亚的希拉波利斯）的北广场挖掘出了哪些雕像？",
#   "研究中使用了哪些实验室分析技术来检测雕像上的微样本？",
#   "在Hierapolis of Phrygia（弗里吉亚的希拉波利斯）的研究中，发现的颜色材料包括哪些？",
#   "Hierapolis of Phrygia（弗里吉亚的希拉波利斯）的雕像上使用了哪些类型的有机染料？",
#   "Hierapolis of Phrygia（弗里吉亚的希拉波利斯）的雕像中，哪些使用了埃及蓝？",
#   "Hierapolis of Phrygia（弗里吉亚的希拉波利斯）的雕像中，哪些使用了茜草红？",
#   "研究中如何处理从雕像上采集的微样本？",
#   "Hierapolis of Phrygia（弗里吉亚的希拉波利斯）的雕像中，哪些部位的颜色保存得较好？",
#   "Hierapolis of Phrygia（弗里吉亚的希拉波利斯）的雕像上发现了哪些类型的涂层？",
#   "Hierapolis of Phrygia（弗里吉亚的希拉波利斯）的雕像上的涂层有何文化意义？",
#   "研究中遇到的光照和环境干扰问题有哪些？",
#   "Hierapolis of Phrygia（弗里吉亚的希拉波利斯）的雕像上，哪些部分的颜色最为显著？",
#   "Hierapolis of Phrygia（弗里吉亚的希拉波利斯）的雕像上，哪些部位的色彩痕迹最为丰富？",
#   "Hierapolis of Phrygia（弗里吉亚的希拉波利斯）的雕像中，哪些使用了多色装饰？",
#   "研究中使用了哪些技术来检测雕像上的有机材料？",
#   "Hierapolis of Phrygia（弗里吉亚的希拉波利斯）的雕像上的有机材料有何特点？",
#   "研究中如何识别雕像上的有机染料？",
#   "Hierapolis of Phrygia（弗里吉亚的希拉波利斯）的雕像上，哪些部分的颜色最难以检测？",
#   "Hierapolis of Phrygia（弗里吉亚的希拉波利斯）的雕像中，哪些类型的颜色材料最常见？",
#   "Hierapolis of Phrygia（弗里吉亚的希拉波利斯）的雕像中，哪些部分的颜色材料保存最完整？",
#   "研究中发现了哪些类型的矿物涂层？",
#   "Hierapolis of Phrygia（弗里吉亚的希拉波利斯）的雕像上，哪些部分的颜色最为鲜艳？",
#   "Hierapolis of Phrygia（弗里吉亚的希拉波利斯）的雕像上，哪些部分的颜色最为暗淡？",
#   "研究中使用了哪些摄影技术来检测雕像上的颜色痕迹？",
#   "Hierapolis of Phrygia（弗里吉亚的希拉波利斯）的雕像上，哪些部位的颜色最为复杂？",
#   "Hierapolis of Phrygia（弗里吉亚的希拉波利斯）的雕像上，哪些部位的颜色最为单一？",
#   "Hierapolis of Phrygia（弗里吉亚的希拉波利斯）的雕像中，哪些使用了多种着色材料？",
#   "研究中如何处理雕像上的微样本以进行实验室分析？",
#   "Hierapolis of Phrygia（弗里吉亚的希拉波利斯）的雕像上，哪些部位的颜色最能反映古罗马时期的风格？",
#   "研究中使用了哪些技术来检测雕像上的矿物涂层？",
#   "Hierapolis of Phrygia（弗里吉亚的希拉波利斯）的雕像上，哪些部位的颜色最能反映古希腊时期的风格？",
#   "Hierapolis of Phrygia（弗里吉亚的希拉波利斯）的雕像上，哪些部位的颜色最能反映罗马帝国时期的风格？",
#   "研究中使用了哪些技术来检测雕像上的有机涂层？",
#   "Hierapolis of Phrygia（弗里吉亚的希拉波利斯）的雕像上，哪些部位的颜色最能反映东方文化的影响？",
#   "Hierapolis of Phrygia（弗里吉亚的希拉波利斯）的雕像上，哪些部位的颜色最能反映本地文化的影响？",
#   "研究中发现了哪些类型的植物染料？",
#   "Hierapolis of Phrygia（弗里吉亚的希拉波利斯）的雕像上，哪些部位的颜色最能反映古代艺术家的技艺？",
#   "Hierapolis of Phrygia（弗里吉亚的希拉波利斯）的雕像中，哪些颜色材料的稳定性最高？",
#   "Hierapolis of Phrygia（弗里吉亚的希拉波利斯）的雕像中，哪些颜色材料的稳定性最低？",
#   "研究中发现了哪些类型的动物染料？",
#   "Hierapolis of Phrygia（弗里吉亚的希拉波利斯）的雕像上，哪些部位的颜色最能反映宗教主题？",
#   "Hierapolis of Phrygia（弗里吉亚的希拉波利斯）的雕像上，哪些部位的颜色最能反映神话主题？",
#   "Hierapolis of Phrygia（弗里吉亚的希拉波利斯）的雕像上，哪些部位的颜色最能反映历史主题？",
#   "Hierapolis of Phrygia（弗里吉亚的希拉波利斯）的雕像上，哪些部位的颜色最能反映日常生活场景？",
#   "研究中发现了哪些类型的矿物颜料？",
#   "Hierapolis of Phrygia（弗里吉亚的希拉波利斯）的雕像上，哪些部位的颜色最能反映古代艺术家的创新？",
#   "Hierapolis of Phrygia（弗里吉亚的希拉波利斯）的雕像上，哪些部位的颜色最能反映古代艺术家的传统？",
#   "研究中发现了哪些类型的无机涂层？",
#   "Hierapolis of Phrygia（弗里吉亚的希拉波利斯）的雕像上，哪些部位的颜色最能反映古代社会的等级制度？",
#   "Hierapolis of Phrygia（弗里吉亚的希拉波利斯）的雕像上，哪些部位的颜色最能反映古代社会的经济状况？",
#   "研究中使用了哪些技术来检测雕像上的无机颜料？",
#   "Hierapolis of Phrygia（弗里吉亚的希拉波利斯）的雕像上，哪些部位的颜色最能反映古代社会的文化多样性？",
#   "Hierapolis of Phrygia（弗里吉亚的希拉波利斯）的雕像上，哪些部位的颜色最能反映古代社会的宗教信仰？"
# ]
#
# ## 源文章
# # The ancient use of colouring on the marble statues of Hierapolis of Phrygia (Turkey): an integrated multi-analytical approach
#
# # The ancient use of colouring on the marble statues of Hierapolis of Phrygia (Turkey): an integrated multi-analytical approach
#
# Susanna Bracci1 & Silvia Vettori $^2\oplus$ & Emma Cantisani1 & Ilaria Degano3 & Marco Galli4
#
# Received: 22 November 2018 / Accepted: 30 January 2019
# $\copyright$ Springer-Verlag GmbH Germany, part of Springer Nature 2019
#
#
# # Abstract
#
# The interest about the extent of the polychromy of ancient artefacts has increased in the last 10 years, increasing our knowledge on classical art, still often perceived as perfectly white. As a consequence, the development of methodologies allowing the detection and interpretation of the traces of colour remaining on the surfaces of archaeological artefacts has gained momentum. This paper presents the results of a multi-disciplinary research carried out about the painting materials used in producing selected marble statues excavated from the archaeological site of Hierapolis of Phrygia (Turkey), integrating the art-historical approach and the archaeometric data. The artefacts discussed in this paper were excavated in the archaeological site of Hierapolis in the course of several years by the Italian archaeological mission (MAIER). The objects include the reliefs and decorative statuary of the Severan Theatre and the statues excavated from the North Agora of the archaeological site, which are currently preserved in the museum of Hierapolis-Pamukkale. The analytical protocol, based on non-invasive imaging techniques (ultraviolet fluorescence images—UVf and visible induced luminescence—VIL), was performed directly outdoor, in the archaeological site. Few microsamples were selected, collected and subjected to laboratory analyses (XRD, FT-IR, SEM-EDS and HPLC-DAD). The integrated protocol allowed for the identification of the colouring materials used in producing the polychromies under study.
#
# Keywords Ancient colour $\cdot$ Imaging techniques $\cdot$ VIL $\cdot$ Marble statue $\cdot$ Egyptian blue $\cdot$ Madder lake
#
#
# # Introduction
#
# During the last decades, the research on the coloration of Mediterranean art and architecture (in particular, Greek and Roman), still often perceived by the general public as perfectly white, has significantly increased thanks to the efforts of scholars looking for traces of colour on archaeological sculptures (Brinkmann et al. 2004; Brinkmann and KochBrinkmann 2010; Liverani and Santamaria 2014; Santamaria and Morresi 2004; Østergaard 2007; Sargent and Therkildsen 2010; Iannaccone et al. 2015; Kakoulli 2001; Liverani et al. 2013). In most cases, non-invasive and non-destructive techniques are applied to detect the surviving traces of colour, such as ultraviolet fluorescence images (UVf) (Verri et al. 2008; Warda et al. 2012), allowing to detect and map traces of organic materials, including red lakes, due to their characteristic pinkish fluorescence. Visible induced luminescence (VIL) has also been widely applied, since it proved to be able to detect any possible trace of Egyptian blue even if only some small particles were preserved on the surface (Accorsi et al. 2009; Verri 2009; Dyer et al. 2013).
#
# In few cases, when the presence of an organic lake was hypothesised and sampling was allowed, micro-destructive techniques have been applied to better characterise the colouring materials on the statues and bas-reliefs. The most commonly used technique to detect organic dyes and pigment is high-performance liquid chromatography, with either spectrophotometric (diode array, DAD) or mass spectrometric (MS) detectors, after a suitable sample treatment. Several papers highlighted on Hellenistic artefacts the presence of madder lake, characterised by high amounts of purpurin and the absence of alizarin (Fostiridou et al. 2016; Mantzouris and Karapanagiotis 2015; Dyer et al. 2018; Karapanagiotis and Chryssoulakis 2006). In these cases, the absence of alizarin with high amounts of purpurin and pseudopurpurin were considered possible indications of the use of Rubia peregrina or Rubia cordifolia and not the cultivated variety Rubia tinctorum. In some cases, the presence of compounds associated with dyes from coccid insect sources was also assessed simultaneously with madder lake markers (Fostiridou et al. 2016; Mantzouris and Karapanagiotis 2015; Dyer et al. 2018; Andreotti et al. 2017). In few instances reported in the literature, similar amounts of alizarin and purpurin were found (Colombini et al. 2017; Sabatini et al. 2016; Giachi et al. 2009) and in one case (Bartolucci et al. 2007) alizarin only was detected.
#
# Within this context, the possible traces of colour on the sculptures found in the archaeological site of Hierapolis of Phrygia (Pamukkale, Denizli, Turkey) were investigated, in the frame of the Marmora Phrygiae Project (Ismaelli and Scardozzi 2016). During the 2014 and 2015 analytical campaigns (within the Italian archaeological mission - MAIER), investigations were performed in situ to evaluate whether the sculptures were originally painted, by looking for the presence of any residual trace of colour. Moreover, the research aimed at assessing the presence of patinas and/ or other ancient treatment. First, the sculptures and reliefs of the Severan Theatre and the materials from the North Agora (Figs. S1 and S2) were investigated. Close observation of the sculptures and reliefs of the podia in situ and in the Archaeological Museum of Hierapolis-Pamukkale, and advanced photographic techniques (UVf and VIL) were applied on the most promising areas.
#
# The sculpture inside the aedicule on the south side of the Porta Regia represents a standing female figure, larger than life size and conserved almost intact, except for the arms and the head (Fig. S1). This statue from the theatre was identified as an early imperial copy of a famous Hellenistic original (Bejor 1991; Galli 2016) by comparison with two statues from Miletos and Aphrodisias. Specifically, the formal structure, volumes and style of the clothing show that the prototype for the statue of Hierapolis was a sculpture made in Pergamon during the first half of the second century BC. The presence of this sculptural type among the funerary stelae of the so-called Bpriestess of Demeter^ in Smyrna demonstrates that the prototype could be a famous cult statue of the goddess.
#
# The second statue (Fig. S1), occupying the aedicule on the north side of the Porta Regia, represents a young woman wearing a chiton fastened below the breast, a broad cloak and a second smaller fringed cloak that covers her head, leaving the face and her long hair uncovered (Bejor 1991; Galli 2016). The statue is thoroughly carved in every detail (even the back is completely finished) with extraordinary skill. The statue has been recognised as a copy of the type referred to as BFortuna braccio nuovo^, first produced in the second half of the fourth century BC, that was particularly popular in the Imperial period. Compared to most of the preserved exemplars, which often show Fortuna with a cornucopia and a helm, the Hierapolis statue is characterised by a series of original iconographic attributes: the right arm in the gesture of anakalypsis, i.e. the ceremonial unveiling of the bride, the presence of the torch in the left hand, the fringed veil, the peculiar woollen-like infulae decorating the head. The analysis of the late-classical prototype and these significant attributes relate the statue to the image of a Kore-Persephone, as designed in the Hadrianic period (Galli 2016).
#
# The data obtained from the investigation of the statue of the so-called Attis (Fig. S2), conserved in the Archaeological Museum of Hierapolis, are particularly interesting. The sculpture portrays a standing, robust female figure, wearing a long cloak fastened on the right shoulder, a heavy sleeved garment with an apoptygma, i.e. with an overfold and a typical Phrygian cap. The statue possibly represents the personification of the Phrygian ethnos and is dated to the early Severan period (Pellino 2011).
#
# The study of the traces of ancient surface treatments was focused on the reliefs of the frieze of the podia and the Demeter statue through a multidisciplinary approach entailing in situ non-invasive techniques (multispectral photography– UVf).
#
# Specific problems and difficulties were faced in the application of photographic techniques in Hierapolis, since the images were acquired directly in situ, in the theatre and the museum. In the first case, working at night was not allowed and sunlight was a near-constant problem (Fig. 1 a-d). In the case of the museum, the analyses were conducted during opening hours, in the presence of artificial light and tourists (Fig. 1 e, f).
#
# Moreover, micro-invasive analytical methods (i.e. XRD, FT-IR, SEM-EDS, HPLC-DAD and HPLC with mass spectrometric detection) were applied on six samples of patinas from the statue of Demeter and four microsamples of coloured paint from the statues of Kore-Persephone and of the so-called Attis.
#
#
# # Experimental and analytical techniques
#
# Direct acquisition of ultraviolet fluorescence (UVf), visible (Vis) and visible induced luminescence images (VIL) were performed in situ. For the photographic UVf a digital camera Canon EOS 7D (18 Mpixel, CMOS sensor) was used. The camera was equipped with Canon lens EFS $28\ \mathrm{mm\f/3.5-5.6}$
#
# ![](images/de507cbea42f6dae65c5951c2f4d94607f6934d147f08d68a345d029b733fddb.jpg)
# Fig. 1 In situ activities during the analysis of the traces of colour on marble statues: (a-d) at the theatre; (e-f) in the archaeological museum
#
# IS with $\mathrm{B}+\mathrm{W}$ 486 UV/IR blocking filter to cut both ultraviolet reflected and the possible infrared radiation stray generated by the lamps. As sources, two Flash Quantum T5D with $\mathrm{B}+\mathrm{W}$ UV black 403 filters were used. The same set-up was used for visible images the only difference is the removal of filter from the flashes.
#
# For VIL acquisitions, the surfaces were irradiated with visible light by using two flashes Quantum T5D mounted with $\mathsf{B}\mathrm{+}\mathsf{W}\,093$ infrared filters; the infrared emission was collected with a modified (built–in filter for IR removed) Canon EOS 400D (10.1 Mpixel, CMOS sensor) with Canon lens EFS $28~\mathrm{mm}$ fitted with $\mathrm{B}+\mathrm{W}$ 486 UV/IR blocking filter to cut all stray radiation from visible spectrum and thus collecting only infrared luminescence emission. A white plate Spectralon $\textsuperscript{\textregistered}$ was used as reference.
#
# In some specific cases, microsamples were collected for laboratory analyses such as $\mathrm{\DeltaX}$ -ray diffraction (XRD) and Fourier transform infrared spectroscopy (FT-IR) to study the patinas.
#
# Powders obtained from each sample were analysed with a PANalytical diffractometer X’Pert PRO with radiation
#
# $C\mathrm{uK}_{\alpha1}=1.54$ , operating at $40\;\mathrm{kV},$ $30\,\mathrm{mA}$ , investigated range $26\ 3^{\circ}{-70^{\circ}}$ , equipped with $\mathrm{{X}^{\bullet}}$ Celerator multidetector. High score data acquisition and interpretation software for determining the mineralogical composition were used. FT-IR spectra of ancient patinas and treatments were collected with a portable Bruker Optics ALPHA FT-IR Spectrometer equipped with SiC Globar source and a DTGS detector. All spectra were acquired in transmittance mode on micro-samples embedded in KBr disks with a resolution of $4\,\mathrm{cm}^{-1}$ in the $4000{-}400\,\mathrm{cm}^{-1}$ range and 16 scans. The collected IR spectra were processed using OPUS 7.2 software.
#
# For the traces of colour, due to the small amount of material sampled, only scanning electron microscopy coupled with elemental analysis (SEM-EDS) was performed. An environmental scanning electron microscopy (ESEM) mod. Quanta-200 FEI, equipped with a microanalysis $\mathrm{\DeltaX}$ -ray energy dispersive spectroscopy (X-EDS EDAX) was employed. Samples were mounted on a carbon tape and transferred into analysis chamber; the images and spectra were recorded in low vacuum condition $\lvert133\,\mathrm{~Pa})$ .
#
# In one specific case, high-performance liquid chromatography both with Diode Array and high-resolution tandem mass spectrometric detection (HPLC-DAD and HPLC-ESIQ-ToF) were applied.
#
# For the HPLC-DAD analysis, a HPLC consisting of a PU2089 quaternary pump with degasser was used, equipped with an autosampler AS-950 coupled to a spectrophotometric diode array detector MD-2010 (Jasco International Co). The data were processed with ChromNav software. The working conditions were as follows: spectra acquisition in the range of $200{-}650\ \mathrm{nm}$ every $0.8~\mathrm{s}$ with a resolution of $4~\mathrm{nm}$ , liquid chromatographic separation at $30~^{\circ}\mathrm{C}$ on an analytical reverse phase column TC-C18 (2) $(4.6\times150\;\mathrm{mm}$ , particle size $5\;\upmu\mathrm{m}$ , Agilent) with a precolumn TC-C18 (2) $(4.6\times12.5\,\mathrm{mm}$ , particle size $5~{\upmu\mathrm{m}}$ , Agilent), flow rate of $1~\mathrm{mL/min}$ and injection volume $20\,\upmu\mathrm{L}$ . The eluents were as follows: 9(A) trifluoroacetic acid (TFA $0.1\%\ \nu/\nu_{s}$ ) in bidistilled water and (B) TFA $(0.1\%\ \nu/\nu)$ in acetonitrile $\mathrm{CH}_{3}\mathrm{CN}$ , HPLC grade, Sigma-Aldrich, USA). The elution gradient was as follows: $0{-}5\ \mathrm{min}$ , isocratic with $15\%$ B; $5{-}30\ \mathrm{min}$ , linear gradient to $50\%$ B; ${30{\-}40}\,\mathrm{min}$ , linear gradient to $70\%$ B and 41–45 linear gradients to $100\%$ B. Re-equilibration took $15\;\mathrm{min}$ .
#
# For the HPLC-ESI-Q-ToF analyses, an HPLC 1200 Infinity (Agilent Technologies, Palo Alto, CA, USA) coupled to a Jet Stream ESI-Q-ToF (6530 Infinity, Agilent Technologies) detector was used. Mass spectrometer control, data acquisition and data analysis were performed with MassHunter $\ensuremath{\stackrel{\r{\r}}{\mathrm{\boldmath~\scriptstyle\textregistered~}}}$ Workstation Software (B.04.00). The ESI working conditions were the following: drying gas temperature $350\ ^{\circ}\mathrm{C}$ and $10\ \mathrm{L/min}$ flow, capillary voltage $4~\mathrm{kV},$ nebuliser gas pressure 35 psig, sheath gas temperature $375\ ^{\circ}\mathrm{C}$ and $12~\mathrm{L/min}$ flow and fragmentor voltage $175\,\mathrm{~V}.$ High resolution MS and MS/MS spectra (CID voltage $30\;\mathrm{V}$ ) were acquired in negative mode in the range $100{-}1000\ \mathrm{m/z}$ at a scan rate of 1.04 spectra/s. Agilent tuning mix $\mathrm{HP}0321$ (Agilent Technologies) prepared in acetonitrile was used for daily autocalibration. Chromatographic separation was performed on a Zorbax Extend C18 Rapid resolution HT column $(2.1\times50\,\mathrm{\mm}$ , particle size $1.8\,\upmu\mathrm{m})$ , with a Zorbax Eclipsed Plus C18 Analytical Guard Colum $\langle4.6\times$ $12.5\ \mathrm{mm}$ , Agilent Technologies), flow rate $0.2~\mathrm{mL/min}$ and injection volume $10~\upmu\mathrm{L}$ . The eluents were A: formic acid (FA $.\ 0.1\%\nu/\nu)$ ) in LC-MS grade water (Sigma, USA) and B: formic acid (FA $0.1\%\ \nu/\nu_{g}$ ) in acetonitrile $\mathrm{CH}_{3}\mathrm{CN}$ , HPLCMS grade, Sigma, USA). The elution gradient was $15\%$ A for $1\ \mathrm{min}$ , then to $50\%$ A in $2~\mathrm{min}$ , to $70\%$ A in $3\ \mathrm{min}$ , to $90\%$ A in $7\ \mathrm{min}$ , to $100\%$ A in $5\ \mathrm{min}$ and then hold for $2~\mathrm{min}$ ; re-equilibration took $10\ \mathrm{min}$ .
#
# The sample was analysed after extraction by hydrolysis in a methanolic solution. In detail, $200~\upmu\mathrm{L}$ of MeOH/HCl (30:1) solution were added to the sample, and the extraction took place for $60~\mathrm{min}$ at $60~^{\circ}\mathrm{C}$ in an ultrasonic bath. The extract was filtered (PTFE filters, $0.45~{\upmu\mathrm{m}}$ pore size), dried under a gentle stream of $\mathrm{N}_{2}$ and dissolved in $100~\upmu\mathrm{L}$ dimethyl sulfoxide (DMSO; J.T. Baker, Holland).
#
#
# # Results and discussion
#
# """

prompt = """
你好
"""

model_uid = "Qwen2.5-72B-Instruct"
response = client.chat.completions.create(
    model=model_uid,
    messages=[
        {
            "content": prompt,
            "role": "user",
        }
    ],
    max_tokens=20000,
    temperature=0.9
)
print(response.choices[0].message.content)
