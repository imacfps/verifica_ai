import { Component } from "react";

export default class ErrorBoundary extends Component {
  state = { hasError: false };

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error, info) {
    console.error("Erro não tratado na UI:", error, info);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="shell">
          <p className="error-msg">
            Algo deu errado ao renderizar a página. Recarregue e tente novamente.
          </p>
        </div>
      );
    }
    return this.props.children;
  }
}
