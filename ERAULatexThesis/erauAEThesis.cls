% Last updated October 2021
% This is the approved Department of Aerospace Engineering latex template. This was written/copied and pasterd etc. by Ebenezer Gnanamanickam. He makes no claims to the originality of the code. He cannibalized and modified almost all of it. He does not provide LATEX support. But if you ask nicely he is always willing to help WITHIN REASON if you stop by his office. Please do not email him.

\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{erauAEThesis}[2022/02/03 ERAU AE thesis class]

\RequirePackage[utf8]{inputenc}


\LoadClass[12pt]{report}

%\usepackage[document]{ragged2e}
\RequirePackage{float, appendix, titlesec, gensymb, amsfonts, graphicx, amsmath, setspace, fancyhdr, verbatim}

\RequirePackage{hyperref,abstract}
\RequirePackage[paperheight=11in,left=1in,right=1in,top=1in,bottom=1in]{geometry}
\RequirePackage[sort&compress,numbers]{natbib}
%\RequirePackage[nottoc,numbib]{tocbibind}


\bibliographystyle{new-aiaa}
\renewcommand{\bibfont}{\normalsize}
\renewcommand\bibname{\normalsize REFERENCES}


%-------------for Nomenclature--------------------------------------------------
\RequirePackage{nomencl}

%------------ for sideways figure ----------------------------------------------
\RequirePackage{rotating}


\RequirePackage[center]{caption}
\captionsetup[figure]{name=Figure,labelsep=space,labelfont=it}
\captionsetup[table]{name=Table,labelsep=space,labelfont=it}

\RequirePackage{tcolorbox}
\newcommand{\infoBox}[1]{\begin{tcolorbox}[width=\textwidth,colback={blue},outer arc=0mm,colupper=white] #1 \end{tcolorbox}}


\doublespacing

% ------------------ Dedication ------------------
\newcommand{\myDedications}[1]{
\clearpage
\begin{center}
\vspace*{\fill}
\emph{#1}\\
\vspace*{\fill}
\end{center}
\thispagestyle{empty}
}


% ------------------ Acknowledgments ------------------
\newenvironment{myAcknow}
{
    \clearpage
    \phantomsection
    \addcontentsline{toc}{chapter}{ACKNOWLEDGMENTS}
    \begin{centering}
    \textbf{ACKNOWLEDGMENTS}\\
    \end{centering}

    % \pagestyle{fancy}
    % \fancyhf{}
    % \renewcommand{\headrulewidth}{0pt}
    % \fancyhead[R]{\thepage}
    \pagenumbering{roman}
}
{
    \clearpage
}

% ------------------ Abstract ------------------
\newenvironment{myAbstract}
{
    \clearpage
    \phantomsection
    \addcontentsline{toc}{chapter}{ABSTRACT}
    \begin{centering}
    \textbf{ABSTRACT}\\
    \end{centering}

}
{
    \clearpage
}
\renewcommand{\abstractname}{ABSTRACT}

% ------------------ Table of contents ------------------
\newenvironment{myToC}
{
    \clearpage
    \phantomsection
    \renewcommand{\contentsname}{\normalsize \centering 
    TABLE OF CONTENTS}
    \tableofcontents

}
{
    \clearpage
}


% ------------------ List of figures ------------------
\newenvironment{myLoFigs}
{
    \clearpage
    \phantomsection
    \renewcommand{\listfigurename}{\normalsize \centering
        LIST OF FIGURES \\
        Figure \hfill Page}
    \listoffigures
    \addcontentsline{toc}{chapter}{LIST OF FIGURES}
}
{
    \clearpage
}

% ------------------ List of Tables ------------------
\newenvironment{myLoTables}
{
    \clearpage
    \phantomsection
    \renewcommand{\listtablename}{\normalsize \centering
        LIST OF TABLES\\
        Table \hfill Page}
    \listoftables
    \addcontentsline{toc}{chapter}{LIST OF TABLES}
}
{
    \clearpage
}

% ------------------ Nomenclature ------------------
\newenvironment{myNomen}
{
    \clearpage
    \phantomsection
    \makenomenclature
    \renewcommand{\nomname}{\normalsize \centering
    NOMENCLATURE    }
    \addcontentsline{toc}{chapter}{NOMENCLATURE}
}
{
    \clearpage
}


\titleformat{\chapter}
  {\centering\normalfont\fontsize{12}{12}\bfseries}{\thechapter ~}{0.35em}{}
\titleformat{\section}
  {\normalfont\fontsize{12}{12}\bfseries}{\thesection}{0.35em}{}
\titleformat{\subsection}
  {\normalfont\fontsize{12}{12}\bfseries}{\thesubsection}{0.35em}{}
\titleformat{\subsubsection}
  {\normalfont\fontsize{12}{12}\bfseries}{\thesubsubsection}{0pt}{}
  
\titlespacing\chapter{0pt}{-16pt}{0pt plus 2pt minus 2pt}
\titlespacing\section{0pt}{12pt plus 4pt minus 2pt}{0pt plus 2pt minus 2pt}
\titlespacing\subsection{0pt}{12pt plus 4pt minus 2pt}{0pt plus 2pt minus 2pt}
\titlespacing\subsubsection{0pt}{12pt plus 4pt minus 2pt}{0pt plus 2pt minus 2pt}    

% removes dots in TOC, LOF etc.
\renewcommand\@dotsep{10000}


% ------------------ List of publications ------------------
\newenvironment{myPublications}
{
    \clearpage
    \phantomsection
    \addcontentsline{toc}{chapter}{PUBLICATIONS}
    \begin{centering}
    \textbf{PUBLICATIONS}\\
    \end{centering}


}
{
    \clearpage
}




