import { Component, AfterViewInit, OnDestroy, ElementRef, ViewChild, ChangeDetectorRef } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Chess, Square } from 'chess.js';
import { Chessground } from 'chessground';

import type { Api as ChessgroundApi } from 'chessground/api';
import type { Config } from 'chessground/config';
import type { Key } from 'chessground/types';


interface LichessMove {
  uci: string;
  san?: string;
  white: number;
  draws: number;
  black: number;
}

interface WikichessPassage {
  article_id: string;
  text: string;
  url: string;
  score: number;
}

interface YoutubeVideo {
  video_id: string;
  title: string;
  description: string;
  channel: string;
  published_at: string;
  url: string;
  thumbnail: string | null;
}

interface StockfishCandidate {
  [key: string]: unknown;
}

interface AgentResponse {
  source: 'lichess' | 'stockfish';
  moves?: LichessMove[];
  best_move?: string | null;
  evaluation_cp?: number | null;
  candidates?: StockfishCandidate[];

  opening_name?: string | null;
  wikichess_context?: WikichessPassage[];
  youtube_videos?: YoutubeVideo[];
  youtube_error?: string | null;
}

@Component({
  selector: 'app-root',
  standalone: true,
  templateUrl: './app.html',
  styleUrl: './app.scss'
})
export class App implements AfterViewInit, OnDestroy {

  @ViewChild('board', { static: true })
  boardElement!: ElementRef<HTMLElement>;

  private chess = new Chess();
  private board?: ChessgroundApi;

  private readonly apiUrl = '/api/v1/agent/analyze';

  private gameVersion = 0;
  private destroyed = false;

  status = 'À vous de jouer !';
  fen = this.chess.fen();

  thinking = false;
  agentAnalysis: AgentResponse | null = null;
  // Analyse destinée au joueur (Blancs)
  playerAnalysis: AgentResponse | null = null;
  playerAnalysisLoading = false;

  constructor(
    private http: HttpClient,
    private cdr: ChangeDetectorRef
  ) {}

  ngAfterViewInit(): void {
    const config: Config = {
      fen: this.chess.fen(),
      orientation: 'white',
      movable: {
        free: false,
        color: 'white',
        dests: this.getLegalMoves(),
        events: {
          after: (orig: Key, dest: Key) => this.onMove(orig, dest)
        }
      }
    };

    this.board = Chessground(this.boardElement.nativeElement, config);
  }

  private getLegalMoves(): Map<Key, Key[]> {
    const dests = new Map<Key, Key[]>();

    for (const move of this.chess.moves({ verbose: true })) {
      const from = move.from as Key;
      const to = move.to as Key;

      if (!dests.has(from)) {
        dests.set(from, []);
      }

      dests.get(from)!.push(to);
    }

    return dests;
  }

  private onMove(orig: Key, dest: Key): void {
    if (this.thinking || this.chess.turn() !== 'w' || this.chess.isGameOver()) {
      this.updateBoard();
      return;
    }

    try {
      const move = this.chess.move({
        from: orig as Square,
        to: dest as Square,
        promotion: 'q'
      });

      if (!move) {
        this.updateBoard();
        return;
      }

      this.fen = this.chess.fen();

      // Les anciennes recommandations ne correspondent plus à la position.
      this.playerAnalysis = null;
      this.playerAnalysisLoading = false;

      if (this.chess.isGameOver()) {
        this.updateStatus();
        this.updateBoard();
        return;
      }

      this.status = 'Coup joué : ' + move.san + ' — L’agent réfléchit…';
      this.thinking = true;

      this.updateBoard();
      this.cdr.detectChanges();

      this.requestAgentMove();

    } catch {
      this.updateBoard();
    }
  }

  private requestAgentMove(): void {
    const version = this.gameVersion;
    const requestedFen = this.chess.fen();

    this.http.post<AgentResponse>(this.apiUrl, {
      fen: requestedFen,
      question: null
    }).subscribe({
      next: (response) => {
        if (
          this.destroyed ||
          version !== this.gameVersion ||
          requestedFen !== this.chess.fen()
        ) {
          return;
        }

        this.agentAnalysis = response;
        const uci = this.getSafeAgentMove(response);

        if (!uci || !/^[a-h][1-8][a-h][1-8][qrbn]?$/.test(uci)) {
          this.stopWithError('Aucun coup exploitable reçu de l’agent.');
          return;
        }

        try {
          const move = this.chess.move({
            from: uci.slice(0, 2) as Square,
            to: uci.slice(2, 4) as Square,
            promotion: uci.length === 5 ? uci[4] : 'q'
          });

          if (!move) {
            this.stopWithError('Le coup proposé par l’agent est illégal.');
            return;
          }

          this.fen = this.chess.fen();
          this.thinking = false;

          this.updateStatus();

          if (!this.chess.isGameOver()) {
            this.status = 'Agent : ' + move.san + ' — À vous de jouer !';
          }

          this.updateBoard([move.from as Key, move.to as Key]);
          this.cdr.detectChanges();
          // Une fois le coup noir joué, analyser la nouvelle position
          // pour conseiller le joueur (blanc).
          if (!this.chess.isGameOver()) {
              this.requestPlayerAnalysis();
          }

        } catch {
          this.stopWithError('Le coup proposé par l’agent est illégal.');
        }
      },

      error: (error) => {
        if (this.destroyed || version !== this.gameVersion) {
          return;
        }

        console.error('Erreur API agent :', error);
        this.stopWithError('Impossible de contacter l’agent IA.');
      }
    });
  }

  private requestPlayerAnalysis(): void {
    const version = this.gameVersion;
    const requestedFen = this.chess.fen();

    // Les recommandations concernent uniquement les Blancs.
    if (this.chess.turn() !== 'w' || this.chess.isGameOver()) {
      return;
    }

    this.playerAnalysis = null;
    this.playerAnalysisLoading = true;
    this.cdr.detectChanges();

    this.http.post<AgentResponse>(this.apiUrl, {
      fen: requestedFen,
      question: null
    }).subscribe({

      next: (response) => {

        // Ignorer une réponse devenue obsolète.
        if (
          this.destroyed ||
          version !== this.gameVersion ||
          requestedFen !== this.chess.fen()
        ) {
          return;
        }

        this.playerAnalysis = response;
        this.playerAnalysisLoading = false;

        this.cdr.detectChanges();
      },

      error: (error) => {

        // Ne pas afficher d'erreur provenant d'une ancienne partie.
        if (
          this.destroyed ||
          version !== this.gameVersion ||
          requestedFen !== this.chess.fen()
        ) {
          return;
        }

        console.error('Erreur analyse pédagogique :', error);

        this.playerAnalysis = null;
        this.playerAnalysisLoading = false;

        // Une erreur pédagogique ne doit pas bloquer la partie.
        this.cdr.detectChanges();
      }

    });
  }

  // Expliquer les déplacements recommandés au joueur (Blancs)
  describeMove(uci: string): string {

    if (!/^[a-h][1-8][a-h][1-8][qrbn]?$/.test(uci)) {
      return 'Déplacement non disponible';
    }

    const from = uci.slice(0, 2) as Square;
    const to = uci.slice(2, 4) as Square;

    const piece = this.chess.get(from);

    if (!piece || piece.color !== 'w') {
      return `Déplacer une pièce de ${from} vers ${to}`;
    }

    // Petit roque : notation UCI utilisée par Lichess
    if (piece.type === 'k' && from === 'e1' && to === 'h1') {
      return 'Petit roque : déplacer le roi de e1 vers g1 et la tour de h1 vers f1';
    }

    // Grand roque : notation UCI utilisée par Lichess
    if (piece.type === 'k' && from === 'e1' && to === 'a1') {
      return 'Grand roque : déplacer le roi de e1 vers c1 et la tour de a1 vers d1';
    }

    const names: Record<string, string> = {
      p: 'pion',
      n: 'cavalier',
      b: 'fou',
      r: 'tour',
      q: 'dame',
      k: 'roi'
    };

    const name = names[piece.type] ?? 'pièce';

    const capture = this.chess.get(to)
      ? ' (prise possible)'
      : '';

    return `Déplacer votre ${name} de ${from} vers ${to}${capture}`;
  }

  private getSafeAgentMove(response: AgentResponse): string | null {
    const proposedMove = this.selectAgentMove(response);

    const legalMoves = this.chess.moves({ verbose: true });

    if (legalMoves.length === 0) {
      return null;
    }

    // Vérifier le coup proposé par l'agent.
    if (proposedMove) {
      const normalizedMove = proposedMove.toLowerCase();

      const isLegal = legalMoves.some(move => {
        const uci = move.from + move.to + (move.promotion ?? '');
        return uci === normalizedMove;
      });

      if (isLegal) {
        return normalizedMove;
     }
    }

    // Coup de secours : premier coup légal disponible.
    const fallback = legalMoves[0];

    console.warn(
      'Coup agent invalide :',
      proposedMove,
      '— Coup de secours :',
      fallback.san
    );

    return fallback.from + fallback.to + (fallback.promotion ?? '');
  }

  private selectAgentMove(response: AgentResponse): string | null {
    if (response.source === 'stockfish') {
      return response.best_move ?? null;
    }

    if (response.source === 'lichess' && response.moves?.length) {
      const mostPlayed = [...response.moves].sort(
        (a, b) =>
          (b.white + b.draws + b.black) -
          (a.white + a.draws + a.black)
      )[0];

      return mostPlayed.uci;
    }

    return null;
  }

  private stopWithError(message: string): void {
    this.thinking = false;
    this.status = message;

    // Les blancs restent bloqués tant que c'est aux noirs de jouer.
    this.updateBoard();
    this.cdr.detectChanges();
  }

  private updateStatus(): void {
    if (this.chess.isCheckmate()) {
      this.status = 'Échec et mat !';
    } else if (this.chess.isDraw()) {
      this.status = 'Partie nulle !';
    } else if (this.chess.isCheck()) {
      this.status = 'Échec !';
    } else {
      this.status = 'À vous de jouer !';
    }
  }

 private updateBoard(lastMove?: [Key, Key]): void {
  const canPlay =
    !this.thinking &&
    this.chess.turn() === 'w' &&
    !this.chess.isGameOver();

  this.board?.set({
    fen: this.chess.fen(),

    // Synchroniser le tour avec chess.js
    turnColor: this.chess.turn() === 'w' ? 'white' : 'black',

    ...(lastMove ? { lastMove } : {}),

    movable: {
      free: false,
      color: canPlay ? 'white' : undefined,
      dests: canPlay
        ? this.getLegalMoves()
        : new Map<Key, Key[]>()
    }
  });
}

  decodeHtml(text: string): string {
    const textarea = document.createElement('textarea');
    textarea.innerHTML = text;
    return textarea.value;
  }


  resetGame(): void {
    this.gameVersion++;

    this.chess.reset();
    this.fen = this.chess.fen();
    this.status = 'Nouvelle partie !';
    this.thinking = false;
    this.agentAnalysis = null;

    // Réinitialiser également les conseils destinés au joueur (blanc).
    this.playerAnalysis = null;
    this.playerAnalysisLoading = false;

    this.board?.set({
      fen: this.chess.fen(),
      lastMove: undefined,
      selected: undefined,
      movable: {
        color: 'white',
        dests: this.getLegalMoves()
      }
    });

    this.cdr.detectChanges();
  }

  ngOnDestroy(): void {
    this.destroyed = true;
    this.gameVersion++;
    this.board?.destroy();
  }
}