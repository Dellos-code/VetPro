package com.vetpro.controller;

import com.vetpro.model.Hospitalization;
import com.vetpro.service.HospitalizationService;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/hospitalizations")
public class HospitalizationController {

    private final HospitalizationService hospitalizationService;

    public HospitalizationController(HospitalizationService hospitalizationService) {
        this.hospitalizationService = hospitalizationService;
    }

    @PostMapping
    public ResponseEntity<Hospitalization> admitPet(@Valid @RequestBody Hospitalization hospitalization) {
        Hospitalization created = hospitalizationService.admitPet(hospitalization);
        return ResponseEntity.status(HttpStatus.CREATED).body(created);
    }

    @GetMapping("/{id}")
    public ResponseEntity<Hospitalization> getHospitalization(@PathVariable Long id) {
        return hospitalizationService.getHospitalizationById(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    @GetMapping("/pet/{petId}")
    public ResponseEntity<List<Hospitalization>> getByPet(@PathVariable Long petId) {
        return ResponseEntity.ok(hospitalizationService.getHospitalizationsByPet(petId));
    }

    @GetMapping("/current")
    public ResponseEntity<List<Hospitalization>> getCurrentlyAdmitted() {
        return ResponseEntity.ok(hospitalizationService.getCurrentlyAdmitted());
    }

    @PutMapping("/{id}/discharge")
    public ResponseEntity<Hospitalization> dischargePet(@PathVariable Long id) {
        return ResponseEntity.ok(hospitalizationService.dischargePet(id));
    }

    @PutMapping("/{id}/notes")
    public ResponseEntity<Hospitalization> updateNotes(@PathVariable Long id, @RequestBody String notes) {
        return ResponseEntity.ok(hospitalizationService.updateDailyNotes(id, notes));
    }
}
