% ourGreenwayBrand.cls
% A custom LaTeX class for Our Greenway research briefs

\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{ourGreenwayBrand}[2025/08/15 Our Greenway Brand Template]

\DeclareOption*{\PassOptionsToClass{\CurrentOption}{article}}
\ProcessOptions\relax

\LoadClass[11pt]{article}

% Required packages
\usepackage[hyphens]{url}
\usepackage{hyperref}
\hypersetup{breaklinks=true}
\RequirePackage{xcolor}
\RequirePackage{geometry}
\RequirePackage{graphicx}
\RequirePackage{fontspec}
\RequirePackage{tikz}
\RequirePackage{ifthen}
\RequirePackage{setspace}
\RequirePackage{titlesec}
\RequirePackage{fancyhdr}
\RequirePackage{afterpage}

\geometry{
    letterpaper,
    top=1.5in,
    bottom=1in,
    left=1in,
    right=1in,
    headheight=0.75in,
    headsep=0.25in
}

% Brand guidelines
\definecolor{BrandGreen}{HTML}{3A5F3A}
\definecolor{BrandGray}{HTML}{4A4A4A}
\definecolor{BrandLight}{HTML}{F2F5F2}
\setmainfont[
  Path=fonts/,
  UprightFont     = *-Regular,
  ItalicFont      = *-Italic,
  BoldFont        = *-Bold,
  BoldItalicFont  = *-BoldItalic
]{DMSans}

% Doc metadata vars
\newcommand{\@headerlabel}{}
\newcommand{\@titletext}{}
\newcommand{\@subtitletext}{}
\newcommand{\@authortext}{}
\newcommand{\@datetext}{}
\newcommand{\@orgtext}{}
\newcommand{\@depttext}{}
\newcommand{\@editedtext}{}

% Metadata cmds
\newcommand{\headerlabel}[1]{\renewcommand{\@headerlabel}{#1}}
\newcommand{\titletext}[1]{\renewcommand{\@titletext}{#1}}
\newcommand{\subtitletext}[1]{\renewcommand{\@subtitletext}{#1}}
\newcommand{\authortext}[1]{\renewcommand{\@authortext}{#1}}
\newcommand{\datetext}[1]{\renewcommand{\@datetext}{#1}}
\newcommand{\orgtext}[1]{\renewcommand{\@orgtext}{#1}}
\newcommand{\editedtext}[1]{\renewcommand{\@editedtext}{#1}}
\newcommand{\depttext}[1]{\renewcommand{\@depttext}{#1}}

\pagestyle{fancy}
\fancyhf{} 

% Header for pages ex. first
\fancyhead[L]{\parbox[t]{2in}{\vspace{0pt}\includegraphics[height=0.3in]{ourGreenwayLogo.png}}}
\fancyhead[R]{\color{BrandGray}\bfseries\parbox[t]{3in}{\vspace{0pt}\raggedleft\@titletext\ - \thepage}}
\renewcommand{\headrulewidth}{0pt}

\fancypagestyle{plain}{
    \fancyhf{}
    \renewcommand{\headrulewidth}{0pt}
}

% Brand title page
\newcommand{\MakeBrandTitle}{
    \thispagestyle{empty}
    
    \mbox{}
    \vspace*{-1in} 
    
    % Green header bar
    \noindent\colorbox{BrandGreen}{%
        \begin{minipage}{\textwidth}
            \vspace{0.1in}
            \hspace{0.5in}%
            \raisebox{-0.15in}{\includegraphics[height=0.4in]{ourGreenwayLogoWhite.png}}%
            \hfill
            {\Large\bfseries\textcolor{white}{\@headerlabel}}%
            \hspace{0.5in}
            \vspace{0.1in}
        \end{minipage}%
    }
    
    
    \noindent\colorbox{BrandLight}{%
        \begin{minipage}{\textwidth}
            \vspace{0.3in}
            \hspace*{0.5in}%
            \begin{minipage}{\dimexpr\textwidth-1in\relax}
                \raggedright
                {\hspace*{0.09in}\Huge\bfseries\color{BrandGray}\@titletext}

                \vspace{0.1in}

                \ifthenelse{\equal{\@subtitletext}{}}{}{
                    {\hspace*{0.09in}\Large\color{BrandGray}\@subtitletext}
                }

                \vspace{0.3in}

                \begin{tabular}{ll}
                    \textbf{Author:} & \@authortext \\[0.05in]
                    \textbf{Edited by:} & \@editedtext \\[0.05in]
                    \textbf{Date:} & \@datetext

                \end{tabular}
            \end{minipage}%
            \vspace{0.3in}
        \end{minipage}%
    }
    \vspace{0.15in}

}

\titleformat{\section}
    {\Large\bfseries\color{BrandGreen}}
    {\thesection}
    {1em}
    {}

\titleformat{\subsection}
    {\large\bfseries\color{BrandGray}}
    {\thesubsection}
    {1em}
    {}

\titleformat{\subsubsection}
    {\normalsize\bfseries\color{BrandGray}}
    {\thesubsubsection}
    {1em}
    {}

\setstretch{1.2}

\setlength{\itemsep}{0.5em}

\AtBeginDocument{
    \pagenumbering{gobble}
    \newpage
    \pagenumbering{arabic}
    \setcounter{page}{1}
}