(() => {
  const panels = [...document.querySelectorAll("[data-view-panel]")];
  const navButtons = [...document.querySelectorAll("[data-dashboard-view]")];
  const sidebar = document.querySelector("#workspace-sidebar");
  const scrim = document.querySelector(".sidebar-scrim");
  const serviceOptions = [...document.querySelectorAll("[data-service]")];
  let selectedService = "";

  const activateView = (view) => {
    const knownView = panels.some((panel) => panel.dataset.viewPanel === view);
    if (!knownView) return;
    panels.forEach((panel) => { panel.hidden = panel.dataset.viewPanel !== view; });
    navButtons.forEach((button) => {
      const active = button.dataset.dashboardView === view;
      if (button.classList.contains("side-link")) button.classList.toggle("is-active", active);
      button.setAttribute("aria-current", active ? "page" : "false");
    });
    sidebar?.classList.remove("is-open");
    scrim?.classList.remove("is-visible");
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  navButtons.forEach((button) => {
    button.addEventListener("click", () => activateView(button.dataset.dashboardView));
  });
  document.querySelector("[data-sidebar-toggle]")?.addEventListener("click", () => {
    sidebar?.classList.add("is-open");
    scrim?.classList.add("is-visible");
  });
  scrim?.addEventListener("click", () => {
    sidebar?.classList.remove("is-open");
    scrim.classList.remove("is-visible");
  });
  document.querySelector("[data-dismiss-notice]")?.addEventListener("click", (event) => {
    event.currentTarget.closest(".workspace-notice")?.remove();
  });

  const selectedLabel = document.querySelector("[data-selected-label]");
  const continueButton = document.querySelector("[data-continue-service]");
  const formPanel = document.querySelector("[data-service-form-panel]");
  const serviceWorkspace = document.querySelector(".service-workspace");
  const serviceNames = { pan: "PAN Verification", name: "Name Match", address: "Address Match" };

  serviceOptions.forEach((option) => {
    option.addEventListener("click", () => {
      selectedService = option.dataset.service;
      serviceOptions.forEach((card) => {
        const active = card === option;
        card.classList.toggle("is-selected", active);
        card.setAttribute("aria-pressed", String(active));
        const marker = card.querySelector(".service-select-label i");
        if (marker) marker.className = active ? "bi bi-check-circle-fill" : "bi bi-circle";
      });
      if (selectedLabel) selectedLabel.textContent = serviceNames[selectedService];
      if (continueButton) continueButton.disabled = false;
    });
  });

  continueButton?.addEventListener("click", () => {
    if (!selectedService || !formPanel) return;
    serviceWorkspace.hidden = true;
    formPanel.hidden = false;
    formPanel.querySelectorAll("[data-service-form]").forEach((form) => {
      form.hidden = form.dataset.serviceForm !== selectedService;
    });
    formPanel.querySelector("[data-form-title]").textContent = serviceNames[selectedService];
    formPanel.querySelector("[data-form-description]").textContent = `Enter the details for ${serviceNames[selectedService].toLowerCase()}.`;
    formPanel.querySelector(`[data-service-form="${selectedService}"] input, [data-service-form="${selectedService}"] textarea`)?.focus();
  });

  document.querySelector("[data-back-to-services]")?.addEventListener("click", () => {
    formPanel.hidden = true;
    serviceWorkspace.hidden = false;
  });

  document.querySelectorAll("[data-service-form]").forEach((form) => {
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      const submitButton = form.querySelector('[type="submit"]');
      const resultPanel = formPanel.querySelector("[data-service-result]");
      const errorPanel = formPanel.querySelector("[data-service-error]");
      const resultContent = formPanel.querySelector("[data-result-content]");
      submitButton.disabled = true;
      submitButton.dataset.originalText = submitButton.textContent;
      submitButton.textContent = "Processing…";
      errorPanel.hidden = true;
      resultPanel.hidden = true;

      try {
        const payload = Object.fromEntries(new FormData(form).entries());
        const response = await fetch(form.dataset.endpoint, {
          method: "POST",
          credentials: "same-origin",
          headers: { "Content-Type": "application/json", "Accept": "application/json" },
          body: JSON.stringify(payload),
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.response_message || "The verification could not be completed.");
        resultContent.textContent = JSON.stringify(data, null, 2);
        resultPanel.hidden = false;
      } catch (error) {
        errorPanel.textContent = error.message || "A network error occurred. Please try again.";
        errorPanel.hidden = false;
      } finally {
        submitButton.disabled = false;
        submitButton.textContent = submitButton.dataset.originalText;
      }
    });
  });

  document.querySelector("[data-clear-result]")?.addEventListener("click", () => {
    formPanel.querySelector("[data-service-result]").hidden = true;
    formPanel.querySelectorAll("[data-service-form]").forEach((form) => form.reset());
  });

  const search = document.querySelector("[data-history-search]");
  search?.addEventListener("input", () => {
    const needle = search.value.trim().toLowerCase();
    document.querySelectorAll("[data-history-row]").forEach((row) => {
      row.hidden = !row.textContent.toLowerCase().includes(needle);
    });
  });

  document.querySelectorAll("[data-refresh-history]").forEach((button) => {
    button.addEventListener("click", async () => {
      const oldText = button.innerHTML;
      button.disabled = true;
      button.innerHTML = '<i class="bi bi-arrow-clockwise"></i> Loading';
      try {
        const response = await fetch("/serviceResult", { credentials: "same-origin", headers: { "Accept": "application/json" } });
        if (!response.ok) throw new Error("Unable to refresh requests");
        window.location.reload();
      } catch {
        button.innerHTML = oldText;
        button.disabled = false;
      }
    });
  });

  const faceForm = document.querySelector("[data-face-compare-form]");
  if (faceForm) {
    const uploadGrid = faceForm.querySelector("[data-document-upload-grid]");
    const liveInput = faceForm.querySelector("[data-live-image]");
    const liveFileName = faceForm.querySelector("[data-live-file-name]");
    const submit = faceForm.querySelector("[data-face-submit]");
    const errorBox = faceForm.querySelector("[data-face-error]");
    const resultsPanel = document.querySelector("[data-face-results]");
    const uploadState = new Map();
    const documentTitles = {
      PAN_INPUT: "PAN",
      PAN: "PAN",
      AADHAAR_INPUT: "Aadhaar",
      AADHAAR: "Aadhaar",
      VOTER_INPUT: "Voter ID",
      VOTER: "Voter ID",
      DL_INPUT: "Driving licence",
      DL: "Driving licence",
      PASSPORT_INPUT: "Passport",
      PASSPORT: "Passport",
      LIVE: "Live image",
      LIVE_INPUT: "Live image",
    };
    let liveFile = null;
    let resultObjectUrls = [];
    let currentReport = null;

    const showFaceError = (message) => {
      errorBox.textContent = message;
      errorBox.hidden = !message;
    };
    const selectedTypes = () => [...faceForm.querySelectorAll("[data-document-toggle]:checked")]
      .map((toggle) => toggle.dataset.documentToggle);
    const selectedDocumentCount = () => [...uploadState.values()]
      .reduce((total, files) => total + files.length, 0);
    const updateFaceSubmit = () => {
      submit.disabled = !liveFile || selectedDocumentCount() === 0;
    };
    const validImageFile = (file) => {
      if (!file) return "Choose an image file.";
      if (!["image/jpeg", "image/png"].includes(file.type)) return "Choose a PNG or JPEG image.";
      if (file.size > 5 * 1024 * 1024) return "Each image must be 5 MB or smaller.";
      return "";
    };

    const showLiveFile = (file) => {
      const validationError = validImageFile(file);
      if (validationError) {
        liveInput.value = "";
        liveFile = null;
        liveFileName.textContent = "No image selected · PNG/JPEG · 5 MB maximum";
        showFaceError(validationError);
        updateFaceSubmit();
        return;
      }
      liveFile = file;
      liveFileName.textContent = file.name;
      showFaceError("");
      updateFaceSubmit();
    };
    liveInput.addEventListener("change", () => showLiveFile(liveInput.files?.[0]));

    faceForm.querySelectorAll("[data-document-toggle]").forEach((toggle) => {
      toggle.addEventListener("change", () => {
        const imageType = toggle.dataset.documentToggle;
        uploadState.delete(imageType);
        uploadGrid.querySelector(`[data-upload-type="${imageType}"]`)?.remove();
        if (toggle.checked) {
          const uploadRow = document.createElement("div");
          uploadRow.className = "document-file-row";
          uploadRow.dataset.uploadType = imageType;
          const title = document.createElement("label");
          title.className = "document-file-label";
          title.textContent = `${documentTitles[imageType]} photos`;
          const fileInput = document.createElement("input");
          fileInput.type = "file";
          fileInput.multiple = true;
          fileInput.accept = "image/jpeg,image/png";
          fileInput.required = true;
          fileInput.id = `document-files-${imageType}`;
          title.htmlFor = fileInput.id;
          fileInput.setAttribute("aria-label", `${documentTitles[imageType]} document images`);
          const hint = document.createElement("small");
          hint.dataset.fileHint = "";
          hint.textContent = "Choose multiple · PNG/JPEG · 5 MB each";
          fileInput.addEventListener("change", () => {
            const files = [...(fileInput.files || [])];
            const validationError = files.map(validImageFile).find(Boolean);
            if (validationError) {
              uploadState.delete(imageType);
              fileInput.value = "";
              hint.textContent = validationError;
              showFaceError(validationError);
            } else if (selectedDocumentCount() - (uploadState.get(imageType)?.length || 0) + files.length + 1 > 10) {
              uploadState.delete(imageType);
              fileInput.value = "";
              hint.textContent = "Limit is 10 images total, including the live image.";
              showFaceError("Select no more than 10 images in total, including the live image.");
            } else {
              uploadState.set(imageType, files);
              hint.textContent = files.length ? `${files.length} image${files.length === 1 ? "" : "s"} selected` : "Choose multiple · PNG/JPEG · 5 MB each";
              showFaceError("");
            }
            updateFaceSubmit();
          });
          uploadRow.append(title, fileInput, hint);
          uploadGrid.append(uploadRow);
        }
        showFaceError("");
        updateFaceSubmit();
      });
    });

    const readBase64 = (file) => new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => {
        const dataUrl = String(reader.result || "");
        const encoded = dataUrl.slice(dataUrl.indexOf(",") + 1);
        if (!encoded) reject(new Error(`Could not read ${file.name}.`));
        else resolve(encoded);
      };
      reader.onerror = () => reject(new Error(`Could not read ${file.name}.`));
      reader.readAsDataURL(file);
    });

    const renderFaceResults = (responseData, documentFilesByType, liveImage) => {
      currentReport = { responseData, documentFilesByType, liveImage };
      const pairs = resultsPanel.querySelector("[data-face-pairs]");
      const summary = resultsPanel.querySelector("[data-face-summary]");
      resultObjectUrls.forEach((url) => URL.revokeObjectURL(url));
      resultObjectUrls = [];
      pairs.replaceChildren();
      const imageUrlsByResultTitle = new Map();
      Object.entries(documentFilesByType).forEach(([imageType, files]) => {
        files.forEach((file, index) => {
          const objectUrl = URL.createObjectURL(file);
          resultObjectUrls.push(objectUrl);
          const resultTitle = imageType.replace("_INPUT", "") + (index ? `_${index + 1}` : "");
          imageUrlsByResultTitle.set(resultTitle, objectUrl);
        });
      });
      const liveUrl = URL.createObjectURL(liveImage);
      resultObjectUrls.push(liveUrl);
      imageUrlsByResultTitle.set("LIVE", liveUrl);

      const overview = responseData.result?.cf_overview || {};
      const transactionDisplay = resultsPanel.querySelector("[data-face-transaction]");
      if (transactionDisplay) transactionDisplay.textContent = responseData.transaction_id || "—";
      const applicationDisplay = resultsPanel.querySelector("[data-face-application]");
      if (applicationDisplay) applicationDisplay.textContent = faceForm.elements.application_number.value;
      const stateDisplay = resultsPanel.querySelector("[data-face-state]");
      if (stateDisplay) stateDisplay.textContent = faceForm.elements.state.value;
      const productDisplay = resultsPanel.querySelector("[data-face-product]");
      if (productDisplay) productDisplay.textContent = faceForm.elements.product.value;
      const generatedDisplay = resultsPanel.querySelector("[data-face-generated]");
      if (generatedDisplay) generatedDisplay.textContent = new Date().toLocaleString();
      const summaryTable = document.createElement("table");
      summaryTable.className = "face-summary-table";
      summaryTable.setAttribute("aria-label", "Face comparison summary");
      const tableHead = document.createElement("thead");
      const headingRow = document.createElement("tr");
      ["Comparison result", "Count"].forEach((heading) => {
        const cell = document.createElement("th");
        cell.scope = "col";
        cell.textContent = heading;
        headingRow.append(cell);
      });
      tableHead.append(headingRow);
      const tableBody = document.createElement("tbody");
      const summaryMetrics = [
        { label: "Images compared", value: overview.NUM_IMG ?? imageUrlsByResultTitle.size, icon: "bi-images", tone: "is-images" },
        { label: "Matches", value: overview.MATCH, icon: "bi-check-circle-fill", tone: "is-matches" },
        { label: "No matches", value: overview.NO_MATCH, icon: "bi-x-circle-fill", tone: "is-no-matches" },
        { label: "Invalid", value: overview.INVALID, icon: "bi-exclamation-triangle-fill", tone: "is-invalid" },
      ];
      summaryMetrics.forEach(({ label, value, icon, tone }) => {
        const row = document.createElement("tr");
        row.className = tone;
        const labelCell = document.createElement("th");
        labelCell.scope = "row";
        labelCell.className = "face-summary-label";
        const labelIcon = document.createElement("i");
        labelIcon.className = `bi ${icon}`;
        labelIcon.setAttribute("aria-hidden", "true");
        labelCell.append(labelIcon, document.createTextNode(label));
        const valueCell = document.createElement("td");
        valueCell.className = "face-summary-count";
        const numericValue = Number(value ?? 0);
        valueCell.textContent = String(Number.isFinite(numericValue) ? numericValue : 0);
        row.append(labelCell, valueCell);
        tableBody.append(row);
      });
      summaryTable.append(tableHead, tableBody);
      summary.replaceChildren(summaryTable);

      const resultPairs = responseData.result?.cf_result || [];
      resultPairs.forEach((pair) => {
        const item = document.createElement("article");
        item.className = "face-pair-result";
        const titleFor = (title) => {
          if (documentTitles[title]) return documentTitles[title];
          const baseType = Object.keys(documentTitles).find((type) => {
            const shortType = type.replace("_INPUT", "");
            return title === shortType || title.startsWith(`${shortType}_`);
          });
          if (!baseType) return title || "Image";
          const shortType = baseType.replace("_INPUT", "");
          const suffix = title.slice(shortType.length).replace(/^_/, " #");
          return `${documentTitles[baseType]}${suffix}`;
        };
        const sourceLabel = titleFor(pair.SRC_TITLE) || "Image 1";
        const targetLabel = titleFor(pair.TRGT_TITLE) || "Image 2";
        const sourceUrl = imageUrlsByResultTitle.get(pair.SRC_TITLE) || "";
        const targetUrl = imageUrlsByResultTitle.get(pair.TRGT_TITLE) || "";
        const matched = ["MATCH", "SAME_IMAGE"].includes(pair.FLAG);
        const scoreText = `${Number(pair.PERCENT || 0).toFixed(3)}%`;

        const toggle = document.createElement("button");
        toggle.type = "button";
        toggle.className = "face-pair-toggle";
        toggle.setAttribute("aria-expanded", "false");
        const names = document.createElement("span");
        names.className = "face-pair-names";
        names.textContent = `${sourceLabel}  ↔  ${targetLabel}`;
        const score = document.createElement("strong");
        score.className = "face-pair-score";
        score.textContent = scoreText;
        const badge = document.createElement("span");
        badge.className = `face-pair-flag ${matched ? "is-match" : "is-nonmatch"}`;
        badge.textContent = pair.FLAG || "No result";
        const chevron = document.createElement("i");
        chevron.className = "bi bi-chevron-down face-pair-chevron";
        chevron.setAttribute("aria-hidden", "true");
        toggle.append(names, score, badge, chevron);

        const pairPanes = [[sourceUrl, sourceLabel], [targetUrl, targetLabel]].map(([imageUrl, label]) => {
          const imageWrap = document.createElement("div");
          imageWrap.className = "face-pair-image";
          const image = document.createElement("img");
          image.src = imageUrl;
          image.alt = `${label} compared image`;
          const caption = document.createElement("span");
          caption.textContent = label;
          imageWrap.append(image, caption);
          return imageWrap;
        });
        const details = document.createElement("div");
        details.className = "face-pair-details";
        details.hidden = true;
        const center = document.createElement("div");
        center.className = "face-pair-center-result";
        const centerScore = document.createElement("strong");
        centerScore.textContent = scoreText;
        const centerStatus = document.createElement("span");
        centerStatus.className = `face-pair-flag ${matched ? "is-match" : "is-nonmatch"}`;
        centerStatus.textContent = pair.FLAG || "No result";
        center.append(centerScore, centerStatus);
        details.append(pairPanes[0], center, pairPanes[1]);
        toggle.addEventListener("click", () => {
          const expanded = toggle.getAttribute("aria-expanded") === "true";
          toggle.setAttribute("aria-expanded", String(!expanded));
          details.hidden = expanded;
          item.classList.toggle("is-expanded", !expanded);
        });
        item.append(toggle, details);
        pairs.append(item);
      });
      const reportLink = resultsPanel.querySelector("[data-face-report]");
      if (reportLink && responseData.transaction_id) {
        reportLink.hidden = false;
      }
      resultsPanel.hidden = false;
      resultsPanel.scrollIntoView({ behavior: "smooth", block: "start" });
    };

    faceForm.addEventListener("submit", async (event) => {
      event.preventDefault();
      const documentTypes = selectedTypes();
      const documentFilesByType = Object.fromEntries(documentTypes
        .filter((imageType) => (uploadState.get(imageType) || []).length)
        .map((imageType) => [imageType, uploadState.get(imageType)]));
      if (!Object.keys(documentFilesByType).length || !liveFile) {
        showFaceError("Upload at least one document image and the required live image.");
        return;
      }

      showFaceError("");
      submit.disabled = true;
      submit.innerHTML = '<i class="bi bi-arrow-repeat"></i> Comparing faces…';
      resultsPanel.hidden = true;
      try {
        const payload = {};
        await Promise.all(Object.entries(documentFilesByType).map(async ([imageType, files]) => {
          payload[imageType] = await Promise.all(files.map(readBase64));
        }));
        payload.LIVE_INPUT = await readBase64(liveFile);
        payload.application_number = faceForm.elements.application_number.value.trim();
        payload.state = faceForm.elements.state.value;
        payload.product = faceForm.elements.product.value;
        const csrfToken = faceForm.querySelector('[name="csrfmiddlewaretoken"]')?.value;
        const response = await fetch("/cface", {
          method: "POST",
          credentials: "same-origin",
          headers: {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-CSRFToken": csrfToken || "",
          },
          body: JSON.stringify(payload),
        });
        const responseData = await response.json();
        if (!response.ok || !responseData.success) {
          throw new Error(responseData.response_message || "Face comparison could not be completed.");
        }
        renderFaceResults(responseData, documentFilesByType, liveFile);
      } catch (error) {
        showFaceError(error.message || "A network error occurred. Please try again.");
      } finally {
        submit.innerHTML = '<i class="bi bi-scan-face"></i> Compare faces';
        updateFaceSubmit();
      }
    });

    const reportLink = resultsPanel.querySelector("[data-face-report]");
    reportLink?.addEventListener("click", async (event) => {
      event.preventDefault();
      if (!currentReport || reportLink.classList.contains("is-loading")) return;

      const originalContent = reportLink.innerHTML;
      reportLink.setAttribute("aria-disabled", "true");
      reportLink.classList.add("is-loading");
      reportLink.innerHTML = '<i class="bi bi-arrow-repeat"></i> Preparing PDF…';
      showFaceError("");
      try {
        const images = {};
        await Promise.all(Object.entries(currentReport.documentFilesByType).map(async ([imageType, files]) => {
          images[imageType] = await Promise.all(files.map(readBase64));
        }));
        images.LIVE_INPUT = await readBase64(currentReport.liveImage);
        const csrfToken = faceForm.querySelector('[name="csrfmiddlewaretoken"]')?.value;
        const response = await fetch("/pdfReport/", {
          method: "POST",
          credentials: "same-origin",
          headers: {
            "Content-Type": "application/json",
            "Accept": "application/pdf, application/json",
            "X-CSRFToken": csrfToken || "",
          },
          body: JSON.stringify({
            transaction_id: currentReport.responseData.transaction_id,
            result: currentReport.responseData.result,
            report_metadata: currentReport.responseData.report_metadata || {
              application_number: faceForm.elements.application_number.value.trim(),
              state: faceForm.elements.state.value,
              product: faceForm.elements.product.value,
            },
            images,
          }),
        });
        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          throw new Error(errorData.response_message || "The PDF report could not be downloaded.");
        }
        if (!response.headers.get("Content-Type")?.includes("application/pdf")) {
          throw new Error("The server did not return a PDF. Please retry the download.");
        }

        const pdfUrl = URL.createObjectURL(await response.blob());
        const download = document.createElement("a");
        download.href = pdfUrl;
        download.download = `Cface_Result_${currentReport.responseData.transaction_id}.pdf`;
        document.body.append(download);
        download.click();
        download.remove();
        window.setTimeout(() => URL.revokeObjectURL(pdfUrl), 1000);
      } catch (error) {
        showFaceError(error.message || "The PDF report could not be downloaded.");
      } finally {
        reportLink.removeAttribute("aria-disabled");
        reportLink.classList.remove("is-loading");
        reportLink.innerHTML = originalContent;
      }
    });

    document.querySelector("[data-clear-face-results]")?.addEventListener("click", () => {
      resultsPanel.hidden = true;
      currentReport = null;
      const reportLink = resultsPanel.querySelector("[data-face-report]");
      if (reportLink) {
        reportLink.hidden = true;
        reportLink.removeAttribute("href");
      }
      resultObjectUrls.forEach((url) => URL.revokeObjectURL(url));
      resultObjectUrls = [];
      resultsPanel.querySelector("[data-face-pairs]").replaceChildren();
    });
  }
})();