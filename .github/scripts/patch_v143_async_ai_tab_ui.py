from __future__ import annotations

from pathlib import Path


PAGE = Path("app/ai-tab/page.js")

START_MARKER = "  const requestTabAnalysis =\n"
END_MARKER = "    /* -----------------------------\n     WATERMARKED PREVIEW PDF\n"

REPLACEMENT = r'''  const requestTabAnalysis =
    async ({
      source,
      audioUrl = null,
      pathname = null,
    }) => {
      const endpoint = '/api/analyze-audio-tab';

      const sendAnalyzerRequest =
        async (payload) => {
          const response = await fetch(
            endpoint,
            {
              method: 'POST',

              headers: {
                'Content-Type':
                  'application/json',
              },

              body: JSON.stringify(
                payload
              ),
            }
          );

          const data = await response
            .json()
            .catch(() => ({}));

          return {
            response,
            data,
          };
        };

      const analysisRequest = {
        source,
        audioUrl,
        pathname,
        song:
          songTitle.trim(),
        artist:
          artistName.trim(),
        transcriptionType:
          selectedType,
        customerEmail:
          customerEmail.trim(),
      };

      setStatusMessage(
        selectedType === 'rhythm'
          ? 'Starting your Rhythm Guitar analysis...'
          : 'Analyzing your uploaded audio...'
      );

      let {
        response,
        data,
      } = await sendAnalyzerRequest(
        analysisRequest
      );

      if (
        response.status === 202 &&
        selectedType === 'rhythm'
      ) {
        const jobToken =
          data?.analysisJob?.token;

        if (!jobToken) {
          throw new Error(
            'The analyzer did not return a valid Rhythm job.'
          );
        }

        const startedAt = Date.now();
        const clientDeadline =
          startedAt +
          21 * 60 * 1000;

        let pollAfterMs = Math.max(
          1500,
          Math.min(
            5000,
            Number(
              data?.analysisJob
                ?.pollAfterMs
            ) || 3000
          )
        );

        while (
          Date.now() < clientDeadline
        ) {
          const elapsedSeconds =
            Math.max(
              0,
              Math.floor(
                (Date.now() -
                  startedAt) /
                  1000
              )
            );

          if (elapsedSeconds < 60) {
            setStatusMessage(
              'Separating instruments and building your Rhythm Guitar tab...'
            );
          } else {
            const elapsedMinutes =
              Math.max(
                1,
                Math.floor(
                  elapsedSeconds / 60
                )
              );

            setStatusMessage(
              `Your Rhythm Guitar tab is still processing (${elapsedMinutes} min). You can keep this page open while the analysis finishes.`
            );
          }

          await new Promise(
            (resolve) => {
              window.setTimeout(
                resolve,
                pollAfterMs
              );
            }
          );

          ({
            response,
            data,
          } = await sendAnalyzerRequest({
            operation: 'status',
            jobToken,
            transcriptionType:
              selectedType,
          }));

          if (
            response.status === 202
          ) {
            pollAfterMs =
              Math.max(
                1500,
                Math.min(
                  5000,
                  Number(
                    data?.analysisJob
                      ?.pollAfterMs
                  ) || pollAfterMs
                )
              );
            continue;
          }

          if (!response.ok) {
            throw new Error(
              data.error ||
                data.message ||
                'The analyzer could not generate tablature.'
            );
          }

          if (
            !data.generatedTab ||
            typeof data.generatedTab !==
              'string'
          ) {
            throw new Error(
              'The analyzer returned no tablature.'
            );
          }

          // The completed result has now crossed the browser boundary safely.
          // Acknowledge deletion of the transient Modal Queue partition. Ack
          // failure is non-fatal because the partition has a 15-minute TTL.
          try {
            await sendAnalyzerRequest({
              operation: 'ack',
              jobToken,
              transcriptionType:
                selectedType,
            });
          } catch (ackError) {
            console.warn(
              'Async Rhythm result cleanup acknowledgement failed; TTL cleanup remains active.',
              ackError
            );
          }

          return data;
        }

        throw new Error(
          'Your Rhythm Guitar analysis did not finish within the processing window. Please try again.'
        );
      }

      if (!response.ok) {
        throw new Error(
          data.error ||
            data.message ||
            'The analyzer could not generate tablature.'
        );
      }

      if (
        !data.generatedTab ||
        typeof data.generatedTab !==
          'string'
      ) {
        throw new Error(
          'The analyzer returned no tablature.'
        );
      }

      return data;
    };
'''


def main() -> None:
    text = PAGE.read_text(encoding="utf-8")
    start = text.find(START_MARKER)
    if start < 0:
        raise SystemExit("requestTabAnalysis start marker not found")

    end = text.find(END_MARKER, start)
    if end < 0:
        raise SystemExit("preview marker not found")

    current = text[start:end]
    if "const endpoint = '/api/analyze-audio-tab';" not in current:
        raise SystemExit("unexpected requestTabAnalysis body")

    if "operation: 'status'" in current:
        raise SystemExit("async UI patch appears to be already applied")

    updated = text[:start] + REPLACEMENT + text[end:]
    PAGE.write_text(updated, encoding="utf-8")

    check = PAGE.read_text(encoding="utf-8")
    required = [
        "response.status === 202",
        "operation: 'status'",
        "operation: 'ack'",
        "21 * 60 * 1000",
        "15-minute TTL",
        "return data;",
    ]
    for fragment in required:
        if fragment not in check:
            raise SystemExit(f"missing async UI invariant: {fragment}")

    print("patched app/ai-tab/page.js for async Rhythm polling")


if __name__ == "__main__":
    main()
